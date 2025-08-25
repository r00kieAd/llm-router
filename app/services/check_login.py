import os, requests, uuid, traceback
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from data.session_store import token_store

load_dotenv()

def getUser(username: str, password: str):
    try:
        url = f'{os.getenv("DB_API_URI")}{os.getenv("DB_READ")}'
        response = requests.get(url)
        creds = response.json()
        msg = f"user '{username}' not found"
        for cred in creds:
            if cred["username"] == username and cred["password"] == password:
                token = str(uuid.uuid4())
                if not updateToken(username = username, token = token):
                    msg = "Failed to update token"
                    break
                return JSONResponse(status_code=200, content={"verification_passed": True, "token": token})
            elif cred["username"] == username and cred["password"] != password:
                msg = "incorrect password"
        return JSONResponse(status_code=200, content={"verification_passed": False, "msg": msg})
    except Exception as e:
        tb_frames = traceback.extract_tb(e.__traceback__) if hasattr(e, "__traceback__") and e.__traceback__ is not None else []
        line_number = tb_frames[-1].lineno if tb_frames else None
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "line_number": line_number
            }
        )

def getGuest():
    pass

def updateToken(username: str = "NA", token: str = "NA"):
    added = token_store.addToken(username, token)
    return added