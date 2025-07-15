from services.gemini_client import query_gemini
from services.openai_client import query_openai

def route_to_client(prompt: str, client: str, model: str) -> dict:
    if client == "gemini":
        response = query_gemini(prompt, model)
    elif client == "openai":
        response = query_openai(prompt, model)
    else:
        response = "Select a valid client"
        model = None

    return {
        "response": response or "No response returned",
        "model_used": model or "Unknown"
    }