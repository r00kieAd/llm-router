from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
from utils.session_store import token_store
from config.current_llm import CurrentLLM
from rag.rag_engine import retriever_cache
from services.manage_memory import mem_instance

logout_router = APIRouter()
mem = mem_instance

class LogoutInterface(BaseModel):
    username: str
    token: str

@logout_router.post("/logout")
async def logoutProcess(request: LogoutInterface):
    try:
        deleted = token_store.deleteToken(request.username)
        removed = CurrentLLM().removeLLM(user=request.username)
        retriever_removed = retriever_cache.pop(request.username, None) is not None
        memory_cleared, mem_clear_status = mem.clear_memory(username=request.username)
        success = deleted or removed or retriever_removed or memory_cleared
        status_code = 200 if success else 400
        return JSONResponse(status_code=status_code, content={"logged_out": deleted or removed, "memory_status": mem_clear_status})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno if tb else None
        return JSONResponse(status_code=500, content={"logged_out": "logged out with exception", "memory_status": "unknown"})
        # raise HTTPException(status_code=500, detail={"error": str(e), "line_number": {line_number}})
