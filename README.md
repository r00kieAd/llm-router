# llm-router

LLM Router is a FastAPI backend that routes prompts to different Large Language Models (LLMs) such as OpenAI and Gemini. It supports manual, semi-automatic, and fully automatic routing, and can optionally enhance responses using Retrieval-Augmented Generation (RAG).

The system is designed to optimize for usefulness, cost, and reliability, not just raw model capability.

##### "work is in progress so below information is not up to date with the repository"

---

## Features

-  Route prompts dynamically to OpenAI or Gemini based on input
-  RAG support with `.txt` and `.pdf` files
-  Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for embedding
-  Upload files through `/upload`, delete via `/clear-data`
-  Simple `/ask` endpoint to query LLMs with or without RAG

---

## Project Structure

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

Components:
- Confidence-scaled score: Primary capability measure
- Cost penalty: Cost × 0.6 × cost_factor (weighted 60%)
- Latency penalty: Latency × 0.4 (weighted 40%)
- Stability bonus: Stability × 0.25 (weighted 25%, only for hard tasks)

# llm-router (detailed)

- reasoning
- planning
- code_debugging

For these tasks, stability contributes more to the final score.

**Context window guard:**

```
if token_estimate > max_tokens:
    model is disqualified
```

Models with insufficient context windows are automatically excluded.

### 3.5 Ranking and Selection

Models are ranked only within the allowed scope:

- Full Auto: All available models compete
- Semi-Auto: Only models from the selected provider
- Manual: No ranking; model is fixed

The highest-scoring model is selected.

**Result example:**

```json
{
  "provider": "OpenAI",
  "model": "gpt-5-mini",
  "mode": "full_auto",
  "score": 8.34,
  "reasoning": "Cost-effective for task type"
}
```

---

## Layer 4: Execution

The routing decision is dispatched to the appropriate execution layer.

**Execution routing:**

- OpenAI models: query_openai()
- Gemini models: query_gemini()

The routing engine never executes models directly. It only produces decisions, which are consumed by execution functions.

---

## Retrieval-Augmented Generation (RAG)

RAG enhances responses by retrieving relevant context from uploaded documents before generating answers.

**RAG components:**

- Embedder: sentence-transformers/all-MiniLM-L6-v2
- Retriever: FAISS-based in-memory retriever (per user)
- Supported formats: .txt and .pdf files

**RAG workflow:**

1. User uploads documents (.txt or .pdf)
2. Documents are embedded and indexed in a user-specific FAISS database
3. When use_rag=true in a request, the prompt is used to retrieve relevant document snippets
4. Retrieved context is prepended to the prompt before sending to the selected model
5. The model generates a response informed by the retrieved documents

**Cache invalidation:**

The retriever cache is invalidated when:
- New files are uploaded
- Files are deleted
- User data is cleared

---

## Routes and Endpoints

All existing routes remain unchanged:

- POST /ask: Submit a prompt and receive a response
- POST /upload: Upload documents for RAG
- DELETE /clear-data: Clear all user data
- POST /authenticate: Authenticate user
- POST /logout: Logout user

**Request payload example (/ask):**

```json
{
  "prompt": "How does photosynthesis work?",
  "mode": "full_auto",
  "use_rag": false,
  "provider": null,
  "model": null
}
```

**Response example:**

```json
{
  "response": "Photosynthesis is a process...",
  "provider": "Gemini",
  "model": "gemini-2.5-pro",
  "routing_mode": "full_auto",
  "task_inferred": "explanation",
  "confidence": 0.95,
  "tokens_used": 245,
  "cost_estimate": 0.12
}
```

---

## Design Principles

1. Scoring functions return scalar values (single numeric scores)
2. Decision functions return structured choices (provider, model, reasoning)
3. Execution functions perform side effects only (no decision-making)
4. Intelligence is budgeted, not maximized (cost is a first-class concern)
5. Transparency: All routing decisions include reasoning and metadata

---

## Current Implementation Status

- Intent-aware routing: Implemented
- Cost-aware auto mode: Implemented
- Task quality caps: Implemented
- Full/semi/manual routing: Implemented
- RAG integration: Implemented
- Metadata and observability: Implemented

---

## Future Extensions

- Memory for better context, Feedback-driven weight tuning
- Tools and Agents
- Local LLM connection
- Model performance tracking (monitor actual performance vs predicted)
- A/B testing framework (compare routing strategies)
- Usage analytics and cost reporting