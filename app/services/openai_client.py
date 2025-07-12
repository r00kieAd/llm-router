import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_openai(prompt: str, model: str) -> str:
    try:
        response = client.responses.create(
            model=model,
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"[OpenAI Error] {str(e)}"