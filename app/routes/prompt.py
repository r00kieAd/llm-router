from fastapi import APIRouter, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.model_router import route_to_client
from rag.rag_engine import build_retriever, augment_prompt_with_context
from utils.session_store import token_store

router = APIRouter()

class AskRequest(BaseModel):
    username: str
    prompt: str
    client: str
    model: str
    top_k: int = 1
    use_rag: bool = False


@router.post("/ask")
async def ask(request: AskRequest, authorization: str = Header(None)):
    try:
        
        authorized = authorizationCheck(request.username, authorization)
        if not authorized:
            return JSONResponse(status_code=401, content={"msg": f"user '{request.username}' is not authorized"})
        if authorized == "err":
            return JSONResponse(status_code=500, content={"msg": f"unable to verify user '{request.username}'"})
        
        retriever = build_retriever(request.username)
        if request.use_rag:
            updated_prompt, rag_used = augment_prompt_with_context(request.prompt, retriever, top_k = request.top_k)
        else:
            updated_prompt = request.prompt
            rag_used = False
        response = route_to_client(updated_prompt, request.client, request.model)
        response["rag_used"] = rag_used
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def authorizationCheck(username, authorization):
    try:
        token = authorization.split("Bearer")[1].strip()
        return token_store.validToken(username, token)
    except Exception as e:
        print(str(e))
        return "err"