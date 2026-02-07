from config.task_quality import taskQuality
TASK_CAP = taskQuality()

def score_model(model_cfg: dict, task_ctx: dict) -> float:
    try:
        primary = task_ctx["primary_task"]
        secondary = task_ctx.get("secondary_tasks", [])
        confidence = task_ctx["confidence"]
        tokens = task_ctx.get("token_estimate", 0)

        score = 0.0
        # score += model_cfg["tasks"].get(primary, 5.0) * 2.0
        raw_task_score = model_cfg["tasks"].get(primary, 5.0)
        cap = TASK_CAP.get(primary, raw_task_score)
        effective_task_score = min(raw_task_score, cap)
        score += effective_task_score * 2.0
        for t in secondary:
            score += model_cfg["tasks"].get(t, 5.0) * 0.5
        score *= (0.5 + confidence)
        if tokens > model_cfg["max_tokens"]:
            return float("-inf")

        cost_factor = cost_sensitivity(task_ctx)
        score -= model_cfg["cost"] * 0.6 * cost_factor

        score -= model_cfg["latency"] * 0.4

        if primary in {"reasoning", "planning", "code_debugging"}:
            score += model_cfg["stability"] * 0.25
        return round(score, 3)

    except Exception as e:
        print("score_model error:", e)
        return float("-inf")
    

def cost_sensitivity(task_ctx):
    tokens = task_ctx["token_estimate"]
    confidence = task_ctx["confidence"]
    primary = task_ctx["primary_task"]
    if primary == "quick_answer" and tokens < 100:
        return 2.5

    if tokens < 300:
        return 1.8

    if confidence < 0.5:
        return 0.8

    return 1.0