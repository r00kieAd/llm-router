# LLM Router

LLM Router is a FastAPI backend that routes prompts to different Large Language Models (LLMs) such as OpenAI and Gemini. It supports manual, semi-automatic, and fully automatic routing, and can optionally enhance responses using Retrieval-Augmented Generation (RAG).

The system is designed to optimize for usefulness, cost, and reliability, not just raw model capability.

---

## Core Capabilities

- Dynamic routing across OpenAI and Gemini
- Three routing modes:
  - Manual: Provider and model fixed by user
  - Semi-Auto: Provider fixed, model auto-selected
  - Full Auto: Provider and model auto-selected
- Intent-aware task analysis
- Cost-aware model selection
- Task quality caps to prevent overpaying for simple tasks
- RAG support with .txt and .pdf files
- FastAPI endpoints for /ask, /upload, /clear-data, authentication, and logout

---

## Project Structure

```
app/
├── main.py
├── routes/
│   ├── prompt.py
│   └── files.py
├── services/
│   ├── model_router.py
│   ├── score_model.py
│   ├── rag_engine.py
│   └── ...
├── rag/
│   ├── embedder.py
│   ├── retriever.py
│   └── rag_engine.py
├── data/
```

---

## Routing Modes

### Manual Routing

Provider and model are explicitly selected by the user. No scoring or inference occurs. The request is executed directly with the specified provider and model.

### Semi-Auto Routing

The provider is fixed by the user (OpenAI or Gemini). The model is automatically selected within that provider only based on scoring analysis.

### Full Auto Routing

Both provider and model are automatically selected. All eligible models compete under a unified scoring function.

---

## Intent-Aware Routing Architecture

Routing is split into four layers that work sequentially to determine the best model for a given prompt.

---

## Layer 1: Prompt Preprocessing

Extracts observable facts from the prompt without performing inference. This layer analyzes structural properties and generates signals for downstream scoring.

**Outputs include:**

- token_estimate: Approximate token count
- Structural signals: Presence of code, math, questions
- Intent surface cues: Observable characteristics from the text
- Length flags: is_short, is_long

**Example:**

Prompt: "How come black holes are smaller than the Sun?"

Derived signals:
- token_estimate: 11
- has_question: true
- is_short: true

---

## Layer 2: Task Inference

Determines what kind of thinking the prompt requires. This layer classifies the primary task and identifies any secondary tasks.

**Supported task types:**

- quick_answer
- explanation
- reasoning
- summarization
- code_generation
- code_debugging
- planning
- long_form_writing

**Output example:**

```json
{
  "primary_task": "quick_answer",
  "secondary_tasks": [],
  "confidence": 1.0
}
```

Confidence reflects the certainty of the inference. Higher confidence means the task classification is more reliable.

---

## Layer 3: Model Scoring and Selection

### 3.1 Model Capability Profiles

Each model has static metadata defining its performance across tasks and operational characteristics.

Example profile:

```json
{
  "provider": "OpenAI",
  "model": "gpt-5",
  "tasks": {
    "reasoning": 9.5,
    "quick_answer": 8.4,
    "code_generation": 9.5
  },
  "cost": 3.9,
  "latency": 3.0,
  "stability": 8.5,
  "max_tokens": 200000
}
```

### 3.2 Task Quality Caps (Diminishing Returns)

Some tasks do not benefit from higher intelligence beyond a certain point. Task quality caps prevent selecting expensive models for tasks that don't require maximum capability.

**Defined caps:**

```
quick_answer: 7.0
summarization: 7.5
explanation: 8.0
code_generation: 8.5
code_debugging: 9.0
reasoning: 9.5
planning: 9.5
long_form_writing: 9.0
```

**Effective task score calculation:**

```
effective_task_score = min(model_task_score, task_quality_cap)
```

This prevents selecting high-cost models for simple tasks. For example, if a quick answer task is routed to GPT-5 (score 9.5), the effective score is capped at 7.0, making it ineligible unless no other options exist.

### 3.3 Cost Sensitivity (Contextual Cost Awareness)

Cost penalties scale based on task difficulty, prompt size, and inference certainty. Cost sensitivity adjusts the weight of cost in the final scoring function.

**Cost sensitivity factor calculation:**

```
cost_factor = 2.5   if task == quick_answer and tokens < 100
            = 1.8   if tokens < 300
            = 0.8   if confidence < 0.5
            = 1.0   otherwise
```

When confidence is low, cost becomes less of a penalty factor. When a task is simple (quick_answer) and the prompt is short (< 100 tokens), cost sensitivity increases to 2.5, strongly discouraging expensive models.

### 3.4 Final Scoring Formula

For each eligible model, a composite score is calculated:

**Base score:**

```
base_score = 2 × effective_primary_task_score
           + 0.5 × sum(secondary_task_scores)
```

The primary task is weighted twice to reflect its importance. Secondary tasks contribute half as much.

**Confidence-scaled score:**

```
confidence_scaled_score = base_score × (0.5 + confidence)
```

A confidence value of 0.5 (low) multiplies the base score by 1.0. A confidence value of 1.0 (high) multiplies by 1.5, boosting the score.

**Final score:**

```
final_score = confidence_scaled_score
            - (cost × 0.6 × cost_factor)
            - (latency × 0.4)
            + (stability × 0.25)
```

Components:
- Confidence-scaled score: Primary capability measure
- Cost penalty: Cost × 0.6 × cost_factor (weighted 60%)
- Latency penalty: Latency × 0.4 (weighted 40%)
- Stability bonus: Stability × 0.25 (weighted 25%, only for hard tasks)

**Hard tasks (higher stability bonus):**

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