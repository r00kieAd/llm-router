import os
from app.rag.embedder import embed_documents, embed_query
from app.rag.retriever import Retriever

def load_documents_from_txt(folder_path: str = "app/data") -> list[str]:
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs

def build_retriever() -> Retriever | None:
    docs = load_documents_from_txt()
    if not docs:
        return None
    embeddings = embed_documents(docs)
    retriever = Retriever()
    retriever.add_documents(embeddings, docs)
    return retriever

def augment_prompt_with_context(query: str, retriever: Retriever | None, top_k: int = 3) -> tuple[str, bool]:
    if retriever is None:
        return query, False
    query_emb = embed_query(query)
    top_chunks = retriever.retrieve(query_emb, top_k=top_k)
    context = "\n---\n".join(top_chunks)
    augmented = f"Context:\n{context}\n\nQuestion:\n{query}"
    return augmented, True