from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_documents(docs: list[str]) -> list[list[float]]:
    return model.encode(docs, convert_to_numpy=True).tolist()

def embed_query(query: str) -> list[float]:
    return model.encode([query], convert_to_numpy=True)[0].tolist()
