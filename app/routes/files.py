from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Form
from fastapi.responses import JSONResponse
from services.file_operations import save_file, clear_files
from utils.session_store import token_store
from rag.rag_engine import retriever_cache

router = APIRouter()

@router.post("/upload")
async def upload_file(username: str = Form(...), authorization: str = Header(None), file: UploadFile = File(...)):
    try:

        authorized = authorizationCheck(username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{username}'"})

        path = save_file(file, username)
        retriever_cache.pop(username, None)
        return {"message": f"File saved to {path}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/clear-data")
async def clear_data(username, authorization: str = Header(None)):
    try:

        authorized = authorizationCheck(username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{username}'"})

        deleted = clear_files(username)
        if username in retriever_cache:
            del retriever_cache[username]
        return {
            "message": f"Deleted {len(deleted)} file(s).",
            "files": deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete files: {str(e)}")


def authorizationCheck(username, authorization):
    try:
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as e:
        print(str(e))
        return "err"
