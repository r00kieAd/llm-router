from config.all_models import available_models
from utils.session_store import token_store
from pydantic import BaseModel
from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse

router = APIRouter()

class Models(BaseModel):
    username: str

@router.post("/all_models")
async def allModels(request: Models, authorization: str = Header(None)):
    try:
        authorized = authorizationCheck(request.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{request.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{request.username}'"})
        
        models = available_models()
        return JSONResponse(status_code=200, content={"models": models})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


def authorizationCheck(username, authorization):
    try:
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as e:
        print(str(e))
        return "err"