from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.services.model_router import route_to_client

app = FastAPI()


class AskRequest(BaseModel):
    prompt: str
    client: str
    model: str


@app.post("/ask")
async def ask(request: AskRequest):
    return route_to_client(request.prompt, request.client, request.model)
