from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import httpx, os, traceback

load_dotenv()
router = APIRouter()

@router.get("/start")
async def start_app():
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.get(os.getenv("DB_API_URI"))
        if 200 <= res.status_code < 300:
            return {"status": "App is awake. DB server active."}
        raise HTTPException(status_code=500, detail="DB server unreachable")
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection Timeout")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))