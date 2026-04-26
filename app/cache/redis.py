import json
import os
import threading
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

try:
    import redis
except Exception:
    print("no redis detected")
    redis = None


load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

_client = None
_client_lock = threading.Lock()
_warned_unavailable = False
_warned_op_error = False


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _redis_enabled() -> bool:
    return _env_bool("REDIS_ENABLED", True)


def _debug_enabled() -> bool:
    if os.getenv("REDIS_DEBUG") is not None:
        return _env_bool("REDIS_DEBUG", False)
    if os.getenv("CACHE_DEBUG") is not None:
        return _env_bool("CACHE_DEBUG", False)
    return False


def _debug_log(msg: str) -> None:
    if _debug_enabled():
        print(msg)


def get_redis_client():
    """
    Lazy Redis client getter for Redis Cloud.

    Env (preferred):
      - REDIS_URL=redis://user:pass@host:port/db
        (if your provider requires TLS, use rediss://... instead)

    Env (fallback):
      - REDIS_HOST, REDIS_PORT, REDIS_DB
    """
    global _client
    if _client is not None:
        return _client

    if redis is None or not _redis_enabled():
        if redis is None:
            _debug_log("[redis] python 'redis' package not available; caching disabled")
        if not _redis_enabled():
            _debug_log("[redis] REDIS_ENABLED=false; caching disabled")
        return None

    with _client_lock:
        if _client is not None:
            return _client

        url = os.getenv("REDIS_URL", "").strip()
        socket_timeout = float(os.getenv("REDIS_SOCKET_TIMEOUT", "2.0"))
        socket_connect_timeout = float(os.getenv("REDIS_CONNECT_TIMEOUT", "2.0"))

        def _build_client(from_url: str):
            return redis.Redis.from_url(
                from_url,
                decode_responses=True,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                retry_on_timeout=True,
            )

        try:
            if url:
                _client = _build_client(url)
            else:
                host = os.getenv("REDIS_HOST", "localhost")
                port = int(os.getenv("REDIS_PORT", "6379"))
                db = int(os.getenv("REDIS_DB", "0"))
                _client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True,
                    socket_timeout=socket_timeout,
                    socket_connect_timeout=socket_connect_timeout,
                    retry_on_timeout=True,
                )

            _client.ping()
            _debug_log("[redis] connected")
            return _client
        except Exception:
            if url.startswith("redis://"):
                try:
                    tls_url = "rediss://" + url[len("redis://") :]
                    _client = _build_client(tls_url)
                    _client.ping()
                    _debug_log("[redis] connected (TLS fallback rediss://)")
                    return _client
                except Exception:
                    pass

            _debug_log("[redis] unable to connect/ping redis; caching disabled")
            _client = None
            return None


def cache_get(key: str) -> Optional[str]:
    global _warned_unavailable, _warned_op_error
    client = get_redis_client()
    if client is None:
        if _debug_enabled() and not _warned_unavailable:
            _warned_unavailable = True
            _debug_log("[redis] client unavailable; all cache ops will be treated as MISS")
        return None
    try:
        return client.get(key)
    except Exception:
        if _debug_enabled() and not _warned_op_error:
            _warned_op_error = True
            _debug_log("[redis] cache_get failed; treating as MISS (check redis connectivity)")
        return None


def cache_set(key: str, value: str, ttl_seconds: Optional[int] = None) -> bool:
    global _warned_unavailable, _warned_op_error
    client = get_redis_client()
    if client is None:
        if _debug_enabled() and not _warned_unavailable:
            _warned_unavailable = True
            _debug_log("[redis] client unavailable; cache writes will be ignored")
        return False
    try:
        if ttl_seconds:
            client.setex(key, int(ttl_seconds), value)
        else:
            client.set(key, value)
        return True
    except Exception:
        if _debug_enabled() and not _warned_op_error:
            _warned_op_error = True
            _debug_log("[redis] cache_set failed; cache writes ignored (check redis connectivity)")
        return False


def cache_delete(key: str) -> bool:
    global _warned_unavailable, _warned_op_error
    client = get_redis_client()
    if client is None:
        if _debug_enabled() and not _warned_unavailable:
            _warned_unavailable = True
            _debug_log("[redis] client unavailable; cache deletes will be ignored")
        return False
    try:
        client.delete(key)
        return True
    except Exception:
        if _debug_enabled() and not _warned_op_error:
            _warned_op_error = True
            _debug_log("[redis] cache_delete failed (check redis connectivity)")
        return False


def cache_get_json(key: str) -> Optional[Any]:
    raw = cache_get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def cache_set_json(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    try:
        raw = json.dumps(value)
    except Exception:
        return False
    return cache_set(key, raw, ttl_seconds=ttl_seconds)
