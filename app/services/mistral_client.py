from mistralai.client import Mistral
import os

api_key = os.getenv("MISTRAL_KEY", "")

if not api_key:
    raise ValueError("MISTRAL_KEY not found")


client = Mistral(api_key=api_key)


def query_mistral_stream(prompt: str, model: str, instruction: str, temperature: float, top_p: float, max_output_token: int):
    try:
        stream = client.chat.stream(
            model=model,
            max_tokens=max_output_token,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            top_p=top_p
        )
        
        for chunk in stream:
            if not chunk or not chunk.data or not chunk.data.choices:
                continue

            choice = chunk.data.choices[0]
            delta = getattr(choice, "delta", None)

            if not delta:
                continue

            text = getattr(delta, "content", None)

            if text:
                yield text
    except Exception as e:
        yield f"[Mistral Error] {str(e)}"
