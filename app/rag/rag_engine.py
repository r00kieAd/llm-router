import os, fitz
from rag.embedder import embed_documents, embed_query
from rag.retriever import Retriever

FILE_DIR = os.path.join(os.getcwd(), "data")
retriever_cache = {}

def load_pdf_content(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def load_documents_from_txt(username, folder_path: str = FILE_DIR) -> list[str]:
    username = os.path.basename(username)
    folder_path = os.path.join(FILE_DIR, username)
    docs = []
    if not os.path.exists(folder_path):
        return docs
    try:
        for filename in os.listdir(folder_path):
            if filename.startswith('.'):
                continue
            full_path = os.path.join(folder_path, filename)
            # print('full_path:', full_path)
            if filename.endswith(".txt"):
                with open(full_path, "r", encoding="utf-8") as f:
                    docs.append(f.read())
            elif filename.endswith(".pdf"):
                docs.append(load_pdf_content(full_path))
            else:
                continue
            # print('updated doc:', docs)
    except Exception as e:
        print(f"Error loading document '{filename}': {e}")
    
    return docs

def build_retriever(username: str = None) -> Retriever | None:
    if not username:
        return
    
    if username in retriever_cache:
        return retriever_cache[username]

    docs = load_documents_from_txt(username)
    if not docs:
        return None
    embeddings = embed_documents(docs)
    retriever = Retriever()
    retriever.add_documents(embeddings, docs)
    retriever_cache[username] = retriever
    return retriever

def augment_prompt_with_context(query: str, retriever: Retriever | None, top_k: int = 1) -> tuple[str, bool]:
    if retriever is None:
        return query, False
    query_emb = embed_query(query)
    top_chunks = retriever.retrieve(query_emb, top_k=top_k)
    context = "\n---\n".join(top_chunks)
    augmented = f"Context:\n{context}\n\nQuestion:\n{query}"
    return augmented, True