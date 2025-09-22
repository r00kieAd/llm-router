from fastapi import APIRouter, HTTPException
from services.check_login import getUser, getGuest
from pydantic import BaseModel
import traceback

auth_router = APIRouter()

class AuthenticateInterface(BaseModel):
    username: str
    password: str
    is_user: bool = True
    ip_value: str = ""

@auth_router.post("/authenticate")
async def authenticate(request: AuthenticateInterface):
    try:
        print(request)
        if request.is_user:
            response = getUser(request.username, request.password)
            return response
        else:
            if request.ip_value:
                response = getGuest(request.ip_value)
            else:
                raise HTTPException(status_code=500, detail={"error": "invalid ip value"})
            return response
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno if tb else None
        raise HTTPException(status_code=500, detail={"error": str(e), "line_number": {line_number}})