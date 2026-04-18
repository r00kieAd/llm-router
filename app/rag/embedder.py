# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('all-MiniLM-L6-v2')

# def embed_documents(docs: list[str]) -> list[list[float]]:
#     return model.encode(docs, convert_to_numpy=True).tolist()

# def embed_query(query: str) -> list[float]:
#     return model.encode([query], convert_to_numpy=True)[0].tolist()

from mistralai.client import Mistral
import os

api_key = os.getenv("MISTRAL_KEY", "")

if not api_key:
    raise ValueError("MISTRAL_KEY not found")


client = Mistral(api_key=api_key)

def embed_documents(docs: list[str]) -> list[list[float]]:
    # print(f'embedding documents: {docs}')
    res = client.embeddings.create(
        model="mistral-embed",
        inputs=docs
    )
    # print(res)
    return [item.embedding for item in res.data]

def embed_query(query: str) -> list[float]:
    res = client.embeddings.create(
        model="mistral-embed",
        inputs=[query]
    )
    return res.data[0].embedding
