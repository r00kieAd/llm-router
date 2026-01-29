from config.model_scores import modelScores
from config.all_models import model_provider
from services.score_model import score_model

AUTO = model_provider("A")


def get_candidate_models(provider_scope: str):
    all_models = modelScores()
    if provider_scope == AUTO:
        return all_models
    return {
        provider_scope: all_models.get(provider_scope, {})
    }


def rank_models(task_ctx: dict, provider_scope: str):
    candidates = get_candidate_models(provider_scope)
    ranked = []

    for models in candidates.values():
        for model_cfg in models.values():
            score = score_model(model_cfg, task_ctx)

            ranked.append({
                "provider": model_cfg["provider"],
                "model": model_cfg["model"],
                "score": score,
            })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    if not ranked:
        raise RuntimeError("No eligible models after provider filtering")

    return {
        "chosen": ranked[0],
        "ranking": ranked,
    }


def select_model(task_ctx: dict, provider_choice: str, model_choice: str):
    print(f'inside select model function....')

    if provider_choice != AUTO and model_choice != AUTO:
        print(f'returning non {AUTO} results')
        return {
            "provider": provider_choice,
            "model": model_choice,
            "mode": "explicit",
        }

    if provider_choice != AUTO and model_choice == AUTO:
        print(f'inside non auto provider and auto model choice....')
        result = rank_models(task_ctx, provider_choice)
        return {
            **result["chosen"],
            "mode": "provider_scoped_auto",
        }

    result = rank_models(task_ctx, AUTO)
    print(f'going full auto....')
    return {
        **result["chosen"],
        "mode": "full_auto",
    }