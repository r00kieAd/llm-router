import os
import requests
import uuid
import traceback
import datetime
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from utils.session_store import token_store
from pathlib import Path

from cache.redis import cache_get, cache_get_json, cache_set, cache_set_json


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


USER_CACHE_TTL_SECONDS = _env_int("USER_CACHE_TTL_SECONDS", 300)
GUEST_CACHE_TTL_SECONDS = _env_int("GUEST_CACHE_TTL_SECONDS", 86400)

_CACHE_DEBUG = _env_bool("CACHE_DEBUG", True)


def _cache_log(msg: str) -> None:
    if _CACHE_DEBUG:
        print(msg)


def _user_cache_key(username: str) -> str:
    return f"db:user:{username}"


def _guest_cache_key(ip_value: str) -> str:
    return f"db:guest_ip:{ip_value}"


def getUser(username: str, password: str):
    try:
        cached_user = cache_get_json(_user_cache_key(username))
        if isinstance(cached_user, dict) and cached_user.get("username") == username and "password" in cached_user:
            if cached_user.get("password") == password:
                _cache_log(f"[cache] HIT user='{username}' -> returning from cache")
                token = str(uuid.uuid4())
                if not updateToken(username=username, token=token):
                    _cache_log(f"[cache] user='{username}' token update failed (cache path)")
                    return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "Failed to update token"})
                return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})

            _cache_log(f"[cache] HIT user='{username}' but password mismatch -> returning from cache")
            return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "incorrect password"})

        _cache_log(f"[cache] MISS user='{username}' -> hitting DB")
        url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_READ_USER")}'
        response = requests.get(url)
        creds = response.json()
        msg = f"user '{username}' not found"
        for cred in creds:
            if cred["username"] == username and cred["password"] == password:
                _cache_log(f"[db] user='{username}' found -> caching and returning from DB")
                cached = cache_set_json(_user_cache_key(username), cred, ttl_seconds=USER_CACHE_TTL_SECONDS)
                if not cached:
                    _cache_log(f"[cache] WRITE-FAIL user='{username}' (db path)")
                token = str(uuid.uuid4())
                if not updateToken(username=username, token=token):
                    _cache_log(f"[db] user='{username}' token update failed (db path)")
                    msg = "Failed to update token"
                    break
                return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})
            elif cred["username"] == username and cred["password"] != password:
                _cache_log(f"[db] user='{username}' found but password mismatch -> caching and returning from DB")
                cached = cache_set_json(_user_cache_key(username), cred, ttl_seconds=USER_CACHE_TTL_SECONDS)
                if not cached:
                    _cache_log(f"[cache] WRITE-FAIL user='{username}' (db path)")
                msg = "incorrect password"
        _cache_log(f"[db] user='{username}' not found / auth failed -> returning from DB")
        return JSONResponse(status_code=200, content={"verification_passed": False, "msg": msg})
    except Exception as e:
        tb_frames = traceback.extract_tb(e.__traceback__) if hasattr(
            e, "__traceback__") and e.__traceback__ is not None else []
        line_number = tb_frames[-1].lineno if tb_frames else None
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "line_number": line_number
            }
        )


def getGuest(ip_value):
    try:
        if cache_get(_guest_cache_key(ip_value)) is not None:
            _cache_log(f"[cache] HIT guest_ip='{ip_value}' -> returning from cache (quota over)")
            return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "guest quota over for this ip"})

        _cache_log(f"[cache] MISS guest_ip='{ip_value}' -> hitting DB")
        url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_READ_GUEST")}'
        response = requests.get(url)
        creds = response.json()
        ip_exists = any(cred.get("ipAddress") == ip_value for cred in creds)
        if ip_exists:
            _cache_log(f"[db] guest_ip='{ip_value}' exists -> caching and returning from DB (quota over)")
            cached = cache_set(_guest_cache_key(ip_value), "1", ttl_seconds=GUEST_CACHE_TTL_SECONDS)
            if not cached:
                _cache_log(f"[cache] WRITE-FAIL guest_ip='{ip_value}' (db path)")
            return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "guest quota over for this ip"})

        _cache_log(f"[db] guest_ip='{ip_value}' not present -> adding guest in DB")
        if not ip_exists:
            curr_timestamp = datetime.datetime.now()
            iso_timestamp = curr_timestamp.isoformat()
            ssid = len(creds) + int(curr_timestamp.strftime("%Y"))
            add_guest_url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_ADD_GUEST")}'
            guest_data = {
                "session_id": ssid,
                "ipAddress": ip_value,
                "lastLogin": iso_timestamp,
                "sessionDuration": 0
            }
            response = requests.post(add_guest_url, json=guest_data)
            if response.status_code == 200:
                token = str(uuid.uuid4())
                if updateToken(username=ip_value, token=token):
                    _cache_log(f"[db] guest_ip='{ip_value}' added -> caching and returning from DB")
                    cached = cache_set(_guest_cache_key(ip_value), "1", ttl_seconds=GUEST_CACHE_TTL_SECONDS)
                    if not cached:
                        _cache_log(f"[cache] WRITE-FAIL guest_ip='{ip_value}' (db path)")
                    return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})
                _cache_log(f"[db] guest_ip='{ip_value}' token update failed (db path)")
                return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "Failed to update token"})
            else:
                _cache_log(f"[db] guest_ip='{ip_value}' add failed -> returning from DB")
                return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "Failed to add guest session"})

        return JSONResponse(status_code=200, content={"verification_passed": False, "msg": "guest quota over for this ip"})
    except Exception as e:
        tb_frames = traceback.extract_tb(e.__traceback__) if hasattr(
            e, "__traceback__") and e.__traceback__ is not None else []
        line_number = tb_frames[-1].lineno if tb_frames else None
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "line_number": line_number
            }
        )


def updateToken(username: str = "NA", token: str = "NA"):
    added = token_store.addToken(username, token)
    return added
