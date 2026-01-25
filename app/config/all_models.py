def available_models():

    models = {
        "ALL": [
            {"id": "A", "name": "Auto"},
            {"id": "M1", "name": "OpenAI"},
            {"id":"M2", "name": "Gemini"}
        ],
        "A": {
            "FOR": "Auto",
            "LIST": []
        },
        "M1": {
            "FOR": "OpenAI",
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
            "FOR": "Gemini",
            "LIST": [
                {"model": "Auto"},
                {"model": "gemini-2.5-flash-lite"},
                {"model": "gemini-2.5-flash"},
                {"model": "gemini-2.5-pro"}
            ]
        }
    }
    return models
