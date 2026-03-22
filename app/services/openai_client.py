import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def query_openai(prompt: str, model: str, instruction: str, temperature: float, top_p: float, max_output_token: int) -> str:
#     try:
#         response = None
#         if "gpt-5" in model:
#             response = client.responses.create(
#                 model=model,
#                 instructions=instruction,
#                 input=prompt,
#                 top_p=top_p,
#                 max_output_tokens=max_output_token
#             )
#         else:
#             response = client.responses.create(
#                 model=model,
#                 instructions=instruction,
#                 input=prompt,
#                 temperature=temperature,
#                 top_p=top_p,
#                 max_output_tokens=max_output_token
#             )
#         return response.output_text if response else "Error"
#     except Exception as e:
#         return f"[OpenAI Error] {str(e)}"

def query_openai_stream(prompt: str, model: str, instruction: str, temperature: float, top_p: float, max_output_token: int):
    try:
        stream_args = {
            "model": model,
            "instructions": instruction,
            "input": prompt,
            "top_p": top_p,
            "max_output_tokens": max_output_token
        }

        if "gpt-5" not in model:
            stream_args["temperature"] = temperature
        with client.responses.stream(**stream_args) as stream:
            for event in stream:
                if event.type != "response.output_text.delta":
                    continue
                delta = event.delta
                if not delta:
                    continue
                if isinstance(delta, dict):
                    delta_text = delta.get("content") or delta.get("text")
                    if not delta_text:
                        delta_text = json.dumps(delta)
                elif isinstance(delta, list):
                    delta_text = "".join(str(part) for part in delta)
                else:
                    delta_text = str(delta)
                if delta_text:
                    yield delta_text
    except Exception as e:
        yield f"[OpenAI Error] {str(e)}"
