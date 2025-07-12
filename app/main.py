from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask(request: AskRequest):
    return {
        "response": f"You asked: {request.prompt}",
        "status": "mocked"
    }
