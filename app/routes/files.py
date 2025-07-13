from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_operations import save_file, clear_files

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        path = save_file(file)
        return {"message": f"File saved to {path}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/clear-data")
async def clear_data():
    try:
        deleted = clear_files()
        print(f"Deleted files: {deleted}")
        return {
            "message": f"Deleted {len(deleted)} file(s).",
            "files": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete files: {str(e)}")
