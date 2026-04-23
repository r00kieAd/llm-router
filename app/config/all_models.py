def model_provider(id):
    match id:
        case "A":
            return "Auto"
        case "M1":
            return "OpenAI"
        case "M2":
            return "Google"
        case "M3":
            return "Mistral"
        case _:
            return None


def available_models():
    models = {
        "ALL": [
            {"id": "A", "name": model_provider("A")},
            {"id": "M1", "name": model_provider("M1")},
            {"id":"M2", "name": model_provider("M2")},
            {"id": "M3", "name": model_provider("M3")}
        ],
        "A": {
            "FOR": model_provider("A"),
            "LIST": []
        },
        "M1": {
            "FOR": model_provider("M1"),
            "LIST": [
                {"model": "Auto"},
                {"model": "gpt-4.1"},
                {"model": "gpt-5"},
                {"model": "gpt-5-nano"},
                {"model": "gpt-5-mini"},
                {"model": "gpt-4.1-mini"}
            ]
        },
        "M2": {
            "FOR": model_provider("M2"),
            "LIST": [
                {"model": "Auto"},
                {"model": "gemini-2.5-flash-lite"},
                {"model": "gemini-2.5-flash"},
                {"model": "gemini-3.1-flash-lite-preview"}
            ]
        },
        "M3": {
            "FOR": model_provider("M3"),
            "LIST": [
                {"model": "Auto"},
                {"model": "open-mistral-nemo"},
                {"model": "labs-leanstral-2603"},
                {"model": "mistral-large-2512"},
                {"model": "mistral-medium-2505"},
                {"model": "ministral-3b-2512"}
            ]
        }
    }
    return models
