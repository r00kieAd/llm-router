# 🧠 llm-router

`llm-router` is a backend application built with FastAPI that allows you to route API requests to different Large Language Models (LLMs) like OpenAI and Gemini, and optionally enhance responses using Retrieval-Augmented Generation (RAG).

##### "work is in progress so below information is not up to date with the repository"

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

[//]: # (This README was expanded by automated analysis of the `app/` package to include detailed RAG, routes, and services documentation.)

# 🧠 llm-router (detailed)

This document explains how the FastAPI backend is wired, how the RAG pieces work, the available HTTP routes with request/response shapes, and what each service does.

Summary: `llm-router` routes prompts to either OpenAI or Google Gemini, optionally augments prompt text using Retrieval-Augmented Generation (RAG) from user-uploaded `.txt` and `.pdf` files, and uses a simple token-based authorization flow.

## Checklist (requirements from your request)
- Analyze `app/` files and extract behavior: Done
- Document `rag/` usage (embedder, retriever, engine): Done
- Document `routes/` endpoints with request & response bodies: Done
- Document `services/` operations and contracts: Done
- Ignore `utils/` internals (auth relies on `token_store` interface): Done

## Quick project layout (what matters)

Relevant files analyzed under `app/`:

- `main.py` — FastAPI app, includes routers from `routes/`
- `rag/embedder.py` — embeddings using `sentence-transformers`
- `rag/retriever.py` — FAISS-based in-memory retriever
- `rag/rag_engine.py` — loads files, builds retriever, augments prompts
- `routes/*.py` — HTTP endpoints (`/start`, `/ask`, `/upload`, `/clear-data`, `/authenticate`, `/logout`)
- `services/*.py` — LLM client wrappers and helpers (`model_router.py`, `openai_client.py`, `gemini_client.py`, `file_operations.py`, `check_login.py`)

## Environment variables (complete)

The app reads the following env vars (see `main.py`, `services/*`):

- `HOST`, `PORT` — used by `main.py` when running directly
- `OPENAI_API_KEY` — `app/services/openai_client.py`
- `GEMINI_API_KEY` — `app/services/gemini_client.py`
- `DB_API_URI`, `DB_READ` — used by `app/services/check_login.py` to fetch stored credentials

Add these to a `.env` at repository root for local testing.

## RAG (retrieval-augmented generation) — design & usage

Files involved:

- `app/rag/embedder.py`
  - Uses `sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')`.
  - Exposes `embed_documents(docs: list[str]) -> list[list[float]]` and `embed_query(query: str) -> list[float]`.

- `app/rag/retriever.py`
  - Wraps a FAISS `IndexFlatL2` index.
  - `Retriever.add_documents(embeddings, docs)` stores embeddings in the index and keeps the raw `docs` list in memory.
  - `Retriever.retrieve(query_embedding, top_k)` returns the top-k document texts (strings).

- `app/rag/rag_engine.py`
  - Loads `.txt` and `.pdf` files from `data/<username>/`.
    - Text files are read directly.
    - PDFs are read with `fitz` (PyMuPDF) page-by-page.
  - `build_retriever(username)`:
    - Loads documents for `username`, computes embeddings with `embed_documents`, creates a `Retriever`, stores it in an in-memory `retriever_cache` keyed by username, and returns it.
    - Returns `None` if there are no docs for the user.
  - `augment_prompt_with_context(query, retriever, top_k=1)`:
    - Embeds the query with `embed_query`, retrieves top_k chunks, joins them with a separator `\n---\n` and returns an augmented prompt of the form:

      Context:
      <chunk1>
      ---
      <chunk2>

      Question:
      <original query>

    - Also returns a boolean indicating whether RAG context was attached.

Notes and behavior:

- RAG supports `.txt` and `.pdf` only.
- Retriever and embeddings are maintained in-memory per username via `retriever_cache`.
- After uploading or clearing files, routes explicitly drop the user's `retriever_cache` entry so a new retriever is built on next `/ask` request.

Security considerations:

- Uploaded files are stored under `data/<username>/`. Filenames starting with `.` are ignored.
- Embeddings and retriever objects live in memory; this repo uses a simple in-process cache without persistence or eviction.

## Routes — endpoints, request and response shapes

All routes are mounted via `main.py` and defined in `app/routes/`.

1) `GET /start`
   - Purpose: healthcheck
   - Request: none
   - Response (200): {"status": "App is awake"}

2) `POST /ask`
   - Handler: `app/routes/prompt.py`
   - Request body (JSON) — Pydantic model `AskRequest`:
     - `username` (str) — username for which to look up RAG files and to validate token
     - `prompt` (str) — the user prompt
     - `client` (str) — "openai" or "gemini" (others return an error-like message)
     - `model` (str) — model identifier sent to the client wrapper
     - `top_k` (int, optional) — how many context chunks to retrieve (default: 1)
     - `use_rag` (bool, optional) — whether to augment the prompt with retrieved context
   - Required header: `Authorization: Bearer <token>`
   - Behavior:
     - Validates token using `token_store.validToken(username, token)` (from `utils/session_store.py`).
     - Builds or retrieves per-user retriever using `build_retriever(username)`.
     - If `use_rag` is true and retriever exists, calls `augment_prompt_with_context` to produce an updated prompt.
     - Calls `services.model_router.route_to_client(updated_prompt, client, model)` and returns the result.
   - Success response (200):
     - `{"response": <text>, "model_used": <model or "Unknown">, "rag_used": <true|false>}`
   - Authorization failure:
     - 401 JSON: {"msg": "user '<username>' is not authorized"}
   - Server error (500):
     - JSON: {"error": "<error string>"}

3) `POST /upload` (multipart/form-data)
   - Handler: `app/routes/files.py`
   - Form fields / headers:
     - `username` (form field) — target user folder
     - `file` (UploadFile) — `.txt` or `.pdf` file
     - `Authorization` header (Bearer token)
   - Behavior:
     - Validates token as in `/ask`.
     - Validates extension (only `.txt` and `.pdf` allowed) and size (max 1 MB).
     - Saves file to `data/<username>/` and removes username from `retriever_cache` so the next `/ask` will rebuild embeddings.
   - Success response (200):
     - `{"message": "File saved to <path>"}`
   - Failure cases:
     - 400 for invalid file/size
     - 401 for unauthorized
     - 500 for unexpected errors

4) `DELETE /clear-data`
   - Handler: `app/routes/files.py`
   - Query parameter: `username` (required)
   - Header: `Authorization: Bearer <token>`
   - Behavior:
     - Validates token.
     - Deletes non-hidden files under `data/<username>/` and clears `retriever_cache` for that user.
   - Success response (200):
     - `{"message": "Deleted <N> file(s).", "files": [<filenames>]}`

5) `POST /authenticate`
   - Handler: `app/routes/authenticate.py`
   - Request body (JSON): `AuthenticateInterface`
     - `username` (str)
     - `password` (str)
     - `is_user` (bool, default true) — only path currently implemented for users
     - `ip_value` (str, optional)
   - Behavior:
     - Calls `services.check_login.getUser(username, password)` which fetches credential list from `DB_API_URI + DB_READ` and compares.
     - On success, `getUser` generates a UUID token, stores it via `token_store.addToken`, and returns:
       - 200 JSON: `{"verification_passed": true, "token": "<uuid>"}`
     - On failure, returns `{"verification_passed": false, "msg": "<reason>"}` with status 200.
   - Error: 500 with error details on exceptions.

6) `POST /logout`
   - Handler: `app/routes/logout.py`
   - Request body (JSON): `LogoutInterface`:
     - `username` (str)
     - `token` (str)
   - Behavior:
     - Calls `token_store.deleteToken(username)`.
     - Returns 200 with `{"logged_out": true}` if deletion succeeded; 202 with `{"logged_out": false}` otherwise.

## Services — what each one does

- `app/services/model_router.py`:
  - Entrypoint for sending prompts to the selected LLM client.
  - `route_to_client(prompt, client, model)`:
    - If `client == "gemini"` calls `services.gemini_client.query_gemini(prompt, model)`.
    - If `client == "openai"` calls `services.openai_client.query_openai(prompt, model)`.
    - Otherwise returns `{"response": "Select a valid client", "model_used": "Unknown"}`.
    - Returns a dictionary with `response` and `model_used`.

- `app/services/openai_client.py`:
  - Uses `openai.OpenAI(api_key=...)` and calls `client.responses.create(model=model, input=prompt)`.
  - Returns `response.output_text` or `"[OpenAI Error] <error>"` on failure.

- `app/services/gemini_client.py`:
  - Uses `google.genai.Client(api_key=...)` and calls `client.models.generate_content(model=model, contents=prompt)`.
  - Returns `response.text` or `"[Gemini Error] <error>"` on failure.

- `app/services/file_operations.py`:
  - Saves uploaded files (only `.txt` and `.pdf`) into `data/<username>/`.
  - Enforces `MAX_SIZE = 1` (MB). If file is larger, raises `ValueError`.
  - `clear_files(username)` removes non-hidden files and returns a list of deleted filenames.

- `app/services/check_login.py`:
  - Fetches credentials from an external DB endpoint (`DB_API_URI + DB_READ`).
  - On matching username/password, generates a UUID token and stores it via `token_store.addToken`.
  - Returns HTTP responses (FastAPI JSONResponse) with verification status and token on success.

## Operational notes, edge-cases and limitations

- Auth: the app relies on `utils.session_store.token_store` to implement `addToken`, `validToken`, and `deleteToken`. The internal implementation of this store was intentionally excluded from analysis, but all routes rely on it for token-based auth.
- Uploaded file size limit is 1 MB. This is small for PDFs — you may want to increase `MAX_SIZE` in `app/services/file_operations.py`.
- RAG pipeline assumes textual chunks fit in memory and does no chunking of large documents; large PDFs can create very large strings which may impact embedding.
- Retriever uses an in-memory FAISS index; restarting the process clears all indices.
- `check_login.getUser` performs a full GET of `DB_READ` and then iterates; ensure that endpoint is secure and paginated if large.
- Error handling: many endpoints return 200 with a JSON failure payload (e.g., authenticate returns 200 with verification_passed=false). Pay attention in client code.

## How to run (short)

1. Create and activate a Python venv (Python 3.10+).
2. Install dependencies from `app/requirements.txt`.
3. Create `.env` with required keys: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DB_API_URI`, `DB_READ`, `HOST`, `PORT` as needed.
4. Run the app:

```bash
python app/main.py   # or
uvicorn app.main:app --reload
```

## Quick examples

- Ask without RAG:

Request (POST /ask):

{
  "username": "alice",
  "prompt": "Summarize the file contents",
  "client": "openai",
  "model": "gpt-4o-mini",
  "use_rag": false
}

Response:

{
  "response": "...",
  "model_used": "gpt-4o-mini",
  "rag_used": false
}

- Ask with RAG (after uploading files for `alice`):

Set `use_rag: true` and optionally `top_k: 2`. The server will build or reuse a retriever for `alice` and prepend context to the prompt.

