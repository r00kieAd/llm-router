from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.model_router import route_to_client
from app.rag.rag_engine import build_retriever, augment_prompt_with_context

router = APIRouter()
retriever = build_retriever()

class AskRequest(BaseModel):
    prompt: str
    client: str
    model: str
    use_rag: bool = False


@router.post("/ask")
async def ask(request: AskRequest):
    try:
        if request.use_rag:
            updated_prompt, rag_used = augment_prompt_with_context(
                request.prompt, retriever)
        else:
            updated_prompt = request.prompt
            rag_used = False
        print("Final prompt:", updated_prompt)
        print("Client:", request.client)
        print("Model:", request.model)
        print("RAG used:", rag_used)
        response = route_to_client(
            updated_prompt, request.client, request.model)
        response["rag_used"] = rag_used
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})