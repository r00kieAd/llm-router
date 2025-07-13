import faiss
import numpy as np

class Retriever:
    def __init__(self, dim: int = 384):
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []
    
    def add_documents(self, embeddings: list[list[float]], docs: list[str]):
        self.index.add(np.array(embeddings).astype("float32"))
        self.documents.extend(docs)
    
    def retrieve(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        query_vector = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_vector, top_k)
        return [self.documents[i] for i in indices[0]]