### 🧠 llm-router

`llm-router` is a backend application built with FastAPI that allows you to route API requests to different Large Language Models (LLMs) like OpenAI and Gemini, and optionally enhance responses using Retrieval-Augmented Generation (RAG).

# "work is in progress so below information is not up to date with the repository"

---

## 🚀 Features

- 🔁 Route prompts dynamically to OpenAI or Gemini based on input
- 📄 RAG support with `.txt` and `.pdf` files
- 🧠 Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for embedding
- 📂 Upload files through `/upload`, delete via `/clear-data`
- 📡 Simple `/ask` endpoint to query LLMs with or without RAG

---

## 📁 Project Structure

```
app/
├── main.py                 # FastAPI app entrypoint
├── data/                # Folder for storing Temporary data to be used by RAG and LLM
├── rag
|   ├── embedder.py         # to embed the documents (if available) and prompt
│   ├── reriever.py         # to retrieve the embeddings and make it as numeric array using numpy
│   └── rag_engine.py       # RAG embedding & prompt context
├── routes/
│   ├── prompt.py           # /ask endpoint
│   └── files.py            # /upload and /clear-data are routed accordingly to file_operaitons.py
|   └── start.py            # app run confirm
├── services/
│   ├── gemini_client.py    # sends generated prompt to gemini and returns the response
│   ├── openai_client.py    # sends generated prompt to openai and returns the response
│   └── model_router.py     # route service to ping the correct llm client as per request
|   └── file_operations.py  # all operations involving upload and delete
```

---

## 📦 Requirements

- Python 3.10+
- `fastapi`, `uvicorn`, `python-multipart`
- `openai`, `google-genai`
- `sentence-transformers`, `PyMuPDF`

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
```

---

## 📡 API Endpoints

### `/ask` (POST)
Send prompt to selected LLM.

```json
{
  "prompt": "Explain transformers",
  "client": "openai",            // or "gemini"
  "model": "any openai model",              // or "gemini model"
  "use_rag": true
}
```

Returns:
```json
{
  "response": "...",
  "model_used": "selected model",
  "rag_used": true // or false if "use_rag" option was opted out or if something went wrong
}
```

---

### `/upload` (POST)
Upload `.txt` or `.pdf` file to use for RAG.

- Form-data key: `file`
- Example: use Postman or curl

```bash
curl -F "file=@yourdoc.pdf" localhost/upload
```

---

### `/clear-data` (DELETE)
Deletes all uploaded files in `app/data/`.

```bash
curl -X DELETE localhost/clear-data
```

---

## 🧪 Testing

- Test LLMs with and without RAG using Postman or frontend
- Upload `.txt`/`.pdf` before enabling `use_rag: true`
- Validate context injection by comparing answers

---

## 🛠️ To Do (Next Steps)

- [ ] Add support for `.md`, `.docx`, `.csv`
- [ ] Implement file-specific RAG selection
- [ ] Deploy to cloud (Render, Vercel, AWS)

---

## 👤 Author

Developed by [@adhyatmadwivedi](https://github.com/r00kieAd) – for personal assistant & AI tooling use-cases.

---
