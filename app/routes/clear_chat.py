from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx, os, traceback
from pydantic import BaseModel
from services.manage_memory import mem_instance

router = APIRouter()
mem = mem_instance

class ClearChatInterface(BaseModel):
    username: str

@router.post("/clear_chat")
async def clear_chat(request: ClearChatInterface):
    try:
        memory_cleared, mem_clear_status = mem.clear_memory(username=request.username)
        status_code = 200 if mem_clear_status else 400
        return JSONResponse(status_code=status_code, content={"memory_status": mem_clear_status, "details": memory_cleared})
    except Exception as e:
        return JSONResponse(status_code=500, content={"memory_status": mem_clear_status if mem_clear_status else False, "details": memory_cleared if memory_cleared else "Unknown"})