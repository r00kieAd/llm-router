# import faiss
import numpy as np

class Retriever:
    # def __init__(self, dim: int = 384):
    #     self.index = faiss.IndexFlatL2(dim)
    #     self.documents = []
    def __init__(self):
        self.embeddings = []
        self.documents = []
    
    def add_documents(self, embeddings: list[list[float]], docs: list[str]):
        # self.index.add(np.array(embeddings).astype("float32"))
        self.embeddings.extend(embeddings)
        self.documents.extend(docs)

    def _cosine_similarity(self, a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def retrieve(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        # query_vector = np.array([query_embedding]).astype("float32")
        # distances, indices = self.index.search(query_vector, top_k)
        # return [self.documents[i] for i in indices[0]]
        scores = []
        for emb in self.embeddings:
            score = self._cosine_similarity(query_embedding, emb)
            scores.append(score)
        
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]