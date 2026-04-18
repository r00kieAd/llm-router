from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
from utils.session_store import token_store
from config.current_llm import CurrentLLM
from rag.rag_engine import retriever_cache

logout_router = APIRouter()

class LogoutInterface(BaseModel):
    username: str
    token: str

@logout_router.post("/logout")
async def logoutProcess(request: LogoutInterface):
    try:
        deleted = token_store.deleteToken(request.username)
        removed = CurrentLLM().removeLLM(user=request.username)
        retriever_removed = retriever_cache.pop(request.username, None) is not None
        success = deleted or removed or retriever_removed
        status_code = 200 if success else 400
        return JSONResponse(status_code=status_code, content={"logged_out": deleted or removed})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno if tb else None
        print(e)
        return JSONResponse(status_code=500, content={"logged_out": "logged out with exception"})
        # raise HTTPException(status_code=500, detail={"error": str(e), "line_number": {line_number}})
