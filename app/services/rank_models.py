from config.model_scores import modelScores
from config.all_models import model_provider
from services.score_model import score_model

AUTO = model_provider("A").lower()


def get_candidate_models(provider_scope: str):
    all_models = modelScores()
    if provider_scope == AUTO:
        return all_models
    return {
        provider_scope: all_models.get(provider_scope, {})
    }


def rank_models(task_ctx: dict, provider_scope: str):
    candidates = get_candidate_models(provider_scope)
    ranked: list[dict] = []
    for models in candidates.values():
        for model_cfg in models.values():
            score = score_model(model_cfg, task_ctx)
            data = {
                "provider": model_cfg["provider"],
                "model": model_cfg["model"],
                "score": score,
            }
            ranked.append(data)

    ranked.sort(key=lambda x: x["score"], reverse=True)
    if not ranked:
        raise RuntimeError("No eligible models after provider filtering")

    return {
        "chosen": ranked[0],
        "ranking": ranked,
    }


def select_model(task_ctx: dict, provider_choice: str, model_choice: str) -> float:
    if provider_choice.lower() != AUTO and model_choice.lower() != AUTO:
        return {
            "provider": provider_choice,
            "model": model_choice,
            "mode": "explicit",
        }

    if provider_choice.lower() != AUTO and model_choice.lower() == AUTO:
        result = rank_models(task_ctx, provider_choice)
        return {
            **result["chosen"],
            "mode": "provider_scoped_auto",
        }

    result = rank_models(task_ctx, AUTO)
    return {
        **result["chosen"],
        "mode": "full_auto",
    }
