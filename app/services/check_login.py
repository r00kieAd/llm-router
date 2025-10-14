import os
import requests
import uuid
import traceback
import datetime
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from utils.session_store import token_store


load_dotenv()


def getUser(username: str, password: str):
    try:
        url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_READ_USER")}'
        response = requests.get(url)
        creds = response.json()
        msg = f"user '{username}' not found"
        for cred in creds:
            if cred["username"] == username and cred["password"] == password:
                token = str(uuid.uuid4())
                if not updateToken(username=username, token=token):
                    msg = "Failed to update token"
                    break
                return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})
            elif cred["username"] == username and cred["password"] != password:
                msg = "incorrect password"
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
        url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_READ_GUEST")}'
        response = requests.get(url)
        creds = response.json()
        allowed = False
        msg = f"guest quota over for this ip"
        print(creds)
        for cred in creds:
            if cred["ipAddress"] == ip_value:
                allowed = False
                break
            else:
                allowed = True
        if allowed:
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
            print(response.json())
            if response.status_code == 200:
                token = str(uuid.uuid4())
                if updateToken(username=ip_value, token=token):
                    return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})
                msg = "Failed to update token"
            else:
                msg = "Failed to add guest session"

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


def updateToken(username: str = "NA", token: str = "NA"):
    added = token_store.addToken(username, token)
    return added
