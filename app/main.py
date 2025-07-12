from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.services.gemini_client import query_gemini

app = FastAPI()

class AskRequest(BaseModel):
    prompt: str
    client: str

@app.post("/ask")
async def ask(request: AskRequest):
    if request.client == "gemini":
        response = query_gemini(request.prompt)
        return {
            "response": response,
            "model_used": "gemini-2.5-flash"
        }
    else:
        response = "api test succeeded"
        return {
            "response": response,
            "model_used": "none"
        }
