import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def query_gemini(prompt: str, model: str, instruction: str, temperature: float, top_p: float, top_k: int, max_output_token: int) -> str:
    try:
        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=temperature,
                topP=top_p,
                topK=top_k,
                maxOutputTokens=max_output_token
                ),
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"[Gemini Error] {str(e)}"
