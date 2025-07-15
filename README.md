# 🧠 llm-router

`llm-router` is a backend application built with FastAPI that allows you to route API requests to different Large Language Models (LLMs) like OpenAI and Gemini, and optionally enhance responses using Retrieval-Augmented Generation (RAG).

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
├── routes/
│   ├── prompt.py           # /ask endpoint
│   └── files.py            # /upload and /clear-data
├── services/
│   ├── model_router.py     # routes requests to correct LLM client
│   ├── file_operations.py  # file save/delete logic
│   └── rag_engine.py       # RAG embedding & prompt context
├── data/                   # Holds uploaded .txt and .pdf files
```

---

## 📦 Requirements

- Python 3.10+
- `fastapi`, `uvicorn`, `python-multipart`
- `openai`, `google-genai`
- `sentence-transformers`, `PyMuPDF`

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```
HOST=your_host_name
PORT=your_port
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

## 🏁 Initialize Project Locally

```bash
$ git clone https://github.com/r00kieAd/llm-router.git
$ python -m venv venv
$ pip install -r requirements
$ python main.py # for custom host and port using .env
$ uvicorn main:app # will give default uri http://127.0.0.1:8000
```

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
