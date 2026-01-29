TASKS = [
    "quick_answer",      # short factual or direct response
    "explanation",       # teaching / why / how
    "reasoning",         # multi-step logic, tradeoffs
    "summarization",     # condense existing content
    "code_generation",   # write or modify code
    "code_debugging",    # fix / analyze code
    "long_form_writing", # essays, blogs, docs
    "planning",          # architecture, steps, design
]

def infer_task(preprocessed: dict) -> dict:
    scores = {task: 0 for task in TASKS}

    signals = preprocessed["signals"]
    cues = preprocessed["intent_cues"]
    tokens = preprocessed["token_estimate"]
    prompt = preprocessed["prompt"].lower()

    if signals["has_code"]:
        scores["code_generation"] += 3
        scores["code_debugging"] += 2

    if cues["mentions_fix"]:
        scores["code_debugging"] += 3

    if cues["mentions_explain"]:
        scores["explanation"] += 3
        scores["reasoning"] += 2

    if signals["has_constraints"]:
        scores["reasoning"] += 2

    if cues["mentions_summarize"]:
        scores["summarization"] += 4

    if tokens < 80:
        scores["quick_answer"] += 3

    if tokens > 300:
        scores["reasoning"] += 2
        scores["planning"] += 1

    if tokens > 800:
        scores["long_form_writing"] += 3
        scores["summarization"] += 2

    if any(k in prompt for k in ["design", "architecture", "approach", "strategy"]):
        scores["planning"] += 3
        scores["reasoning"] += 1

    primary = max(scores, key=scores.get)
    total = sum(scores.values()) or 1

    confidence = scores[primary] / total

    secondary = [
        task for task, score in scores.items()
        if score > 0 and task != primary
    ]

    return {
        "primary_task": primary,
        "secondary_tasks": secondary,
        "confidence": round(confidence, 2),
        "scores": scores,
    }