from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
from data.session_store import token_store

logout_router = APIRouter()

class LogoutInterface(BaseModel):
    username: str
    token: str

@logout_router.post("/logout")
async def logoutProcess(request: LogoutInterface):
    try:
        deleted = token_store.deleteToken(request.username)
        status_code = 200 if deleted else 202
        return JSONResponse(status_code=status_code, content={"logged_out": deleted})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno if tb else None
        raise HTTPException(status_code=500, detail={"error": str(e), "line_number": {line_number}})
