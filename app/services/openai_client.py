import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def query_openai(prompt: str, model: str, instruction: str, temperature: float, top_p: float, max_output_token: int) -> str:
    try:
        response = None
        if "gpt-5" in model:
            response = client.responses.create(
                model=model,
                instructions=instruction,
                input=prompt,
                top_p=top_p,
                max_output_tokens=max_output_token
            )
        else:
            response = client.responses.create(
                model=model,
                instructions=instruction,
                input=prompt,
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_token
            )
        return response.output_text if response else "Error"
    except Exception as e:
        return f"[OpenAI Error] {str(e)}"
