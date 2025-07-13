from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/start")
async def start_app():
    try:
        return {"status": "App is awake"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))