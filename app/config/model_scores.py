from config.all_models import model_provider

OPENAI = model_provider("M1")
GEMINI = model_provider("M2")

def modelScores():
    scores = {
        OPENAI: {
            "gpt-4.1": {
                "provider": OPENAI,
                "model": "gpt-4.1",
                "tasks": {
                    "reasoning": 8.5,
                    "code_generation": 8.5,
                    "code_debugging": 8.5,
                    "planning": 8.5,
                    "summarization": 7.6,
                    "quick_answer": 7.6,
                    "explanation": 8.5,
                    "long_form_writing": 8.5
                },
                "max_tokens": 128000,
                "latency": 2.4,
                "cost": 2.4,
                "stability": 8.5
            },
            "gpt-5": {
                "provider": OPENAI,
                "model": "gpt-5",
                "tasks": {
                    "reasoning": 9.5,
                    "code_generation": 9.5,
                    "code_debugging": 9.5,
                    "planning": 9.5,
                    "summarization": 8.4,
                    "quick_answer": 8.4,
                    "explanation": 9.5,
                    "long_form_writing": 9.5
                },
                "max_tokens": 200000,
                "latency": 3.0,
                "cost": 3.9,
                "stability": 8.5
            },
            "gpt-5-nano": {
                "provider": OPENAI,
                "model": "gpt-5-nano",
                "tasks": {
                    "reasoning": 7.2,
                    "code_generation": 7.2,
                    "code_debugging": 7.2,
                    "planning": 7.2,
                    "summarization": 6.4,
                    "quick_answer": 6.4,
                    "explanation": 7.2,
                    "long_form_writing": 7.2
                },
                "max_tokens": 32000,
                "latency": 1.2,
                "cost": 0.9,
                "stability": 8.5
            },
            "gpt-5-mini": {
                "provider": OPENAI,
                "model": "gpt-5-mini",
                "tasks": {
                    "reasoning": 7.9,
                    "code_generation": 7.9,
                    "code_debugging": 7.9,
                    "planning": 7.9,
                    "summarization": 7.0,
                    "quick_answer": 7.0,
                    "explanation": 7.9,
                    "long_form_writing": 7.9
                },
                "max_tokens": 64000,
                "latency": 1.6,
                "cost": 1.5,
                "stability": 8.5
            },
            "gpt-4.1-mini": {
                "provider": OPENAI,
                "model": "gpt-4.1-mini",
                "tasks": {
                    "reasoning": 7.6,
                    "code_generation": 7.6,
                    "code_debugging": 7.6,
                    "planning": 7.6,
                    "summarization": 6.8,
                    "quick_answer": 6.8,
                    "explanation": 7.6,
                    "long_form_writing": 7.6
                },
                "max_tokens": 64000,
                "latency": 1.4,
                "cost": 1.2,
                "stability": 8.5
            }
        },
        GEMINI: {
            "gemini-2.5-flash-lite": {
                "provider": GEMINI,
                "model": "gemini-2.5-flash-lite",
                "tasks": {
                    "reasoning": 5.2,
                    "code_generation": 5.2,
                    "code_debugging": 5.2,
                    "planning": 5.2,
                    "summarization": 6.8,
                    "quick_answer": 6.8,
                    "explanation": 6.0,
                    "long_form_writing": 6.0
                },
                "max_tokens": 50000,
                "latency": 0.5,
                "cost": 0.4,
                "stability": 7.6
            },
            "gemini-2.5-flash": {
                "provider": GEMINI,
                "model": "gemini-2.5-flash",
                "tasks": {
                    "reasoning": 6.3,
                    "code_generation": 6.3,
                    "code_debugging": 6.3,
                    "planning": 6.3,
                    "summarization": 8.1,
                    "quick_answer": 8.1,
                    "explanation": 7.2,
                    "long_form_writing": 7.2
                },
                "max_tokens": 100000,
                "latency": 0.8,
                "cost": 1.2,
                "stability": 7.6
            },
            "gemini-2.5-pro": {
                "provider": GEMINI,
                "model": "gemini-2.5-pro",
                "tasks": {
                    "reasoning": 7.7,
                    "code_generation": 7.7,
                    "code_debugging": 7.7,
                    "planning": 7.7,
                    "summarization": 9.9,
                    "quick_answer": 9.9,
                    "explanation": 8.8,
                    "long_form_writing": 8.8
                },
                "max_tokens": 200000,
                "latency": 1.8,
                "cost": 3.0,
                "stability": 7.6
            }
        }
    }
    return scores
