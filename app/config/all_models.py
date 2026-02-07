def model_provider(id):
    match id:
        case "A":
            return "Auto"
        case "M1":
            return "OpenAI"
        case "M2":
            return "Gemini"
        case _:
            return None


def available_models():
    models = {
        "ALL": [
            {"id": "A", "name": model_provider("A")},
            {"id": "M1", "name": model_provider("M1")},
            {"id":"M2", "name": model_provider("M2")}
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
                {"model": "gemini-2.5-pro"}
            ]
        }
    }
    return models
