def score_model(model_cfg: dict, task_ctx: dict) -> float:
    score = 0.0

    primary = task_ctx["primary_task"]
    secondary = task_ctx.get("secondary_tasks", [])
    confidence = task_ctx["confidence"]
    tokens = task_ctx["token_estimate"]

    score += model_cfg["tasks"].get(primary, 5.0) * 2.0 # checking primary

    for t in secondary:
        score += model_cfg["tasks"].get(t, 5.0) * 0.5 # checking secondary

    score *= (0.5 + confidence) # calculating confidence

    if tokens > model_cfg["max_tokens"]:
        return float("-inf") # Context window hard gate

    score -= model_cfg["cost"] * 0.6
    score -= model_cfg["latency"] * 0.4

    if primary in {"reasoning", "planning", "code_debugging"}:
        score += model_cfg["stability"] * 0.25

    return round(score, 3)