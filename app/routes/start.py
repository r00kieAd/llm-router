from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import httpx, os, traceback
import asyncio

load_dotenv()
router = APIRouter()

@router.get("/start")
async def start_app():
    try:
        print("pinging db server")
        await asyncio.sleep(8)

        async with httpx.AsyncClient(http2=False, timeout=90.0) as client:
            for i in range(3):
                res = await client.get(
                    os.getenv("DB_API_URI"),
                    headers={
                        "User-Agent": "llm-router-service",
                        "Accept": "*/*"
                    }
                )

                print("Response:", res.status_code, res.text)

                if res.status_code < 429:
                    break

                await asyncio.sleep(2 * (i + 1))
                
        return JSONResponse(status_code=res.status_code, content={"detail": res.text})
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection Timeout")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))