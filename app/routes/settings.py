from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.update_llm_settings import updateUserLLM, updateSettings
from config.llm_config import LLMConfig
from utils.session_store import token_store

settings_router = APIRouter()


class LLMChangeRequest(BaseModel):
    username: str
    llm: str


class LLMSettingsRequest(BaseModel):
    username: str
    temp: float
    top_p: float
    top_k: float
    output_tokens: float
    freq_penalty: float
    presence_penalty: float


@settings_router.post("/update_llm_choice")
async def updateLLMChoice(request: LLMChangeRequest, authorization: str = Header(None)):
    try:
        authorized = authorizationCheck(request.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{request.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{request.username}'"})

        res = updateUserLLM(request.username, request.llm)
        return res

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@settings_router.post("/update_llm_settings")
async def updateLLMSettings(request: LLMSettingsRequest, authorization: str = Header(None)):
    try:

        authorized = authorizationCheck(request.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{request.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{request.username}'"})

        res = updateSettings(request.username, request.temp, request.top_p, request.top_k,
                             request.output_tokens, request.freq_penalty, request.presence_penalty)
        return res
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


def authorizationCheck(username, authorization):
    try:
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as e:
        print(str(e))
        return "err"
