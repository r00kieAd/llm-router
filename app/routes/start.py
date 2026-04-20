from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import httpx, os, traceback

load_dotenv()
router = APIRouter()

@router.get("/start")
async def start_app():
    try:
        async with httpx.AsyncClient(http2=False, timeout=90.0) as client:
            res = await client.get(os.getenv("DB_API_URI"),
            headers={
                "User-Agent": "llm-router-service",
                "Accept": "*/*"
        })
        if 200 <= res.status_code < 300:
            return {"status": "App is awake. DB server active."}
        raise HTTPException(status_code=res.status_code, detail=res.text)
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection Timeout")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))