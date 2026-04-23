from config.all_models import model_provider

OPENAI = model_provider("M1")
GEMINI = model_provider("M2")
MISTRAL = model_provider("M3")

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
            "gemini-3.1-flash-lite-preview": {
                "provider": GEMINI,
                "model": "gemini-3.1-flash-lite-preview",
                "tasks": {
                    "reasoning": 6.8,
                    "code_generation": 6.8,
                    "code_debugging": 6.8,
                    "planning": 6.8,
                    "summarization": 8.6,
                    "quick_answer": 8.6,
                    "explanation": 7.6,
                    "long_form_writing": 7.6
                },
                "max_tokens": 1000000,
                "latency": 0.3,
                "cost": 0.8,
                "stability": 7.9
            }
        },
        MISTRAL: {
            "mistral-large-2512": {
                "provider": MISTRAL,
                "model": "mistral-large-2512",
                "tasks": {
                    "reasoning": 8.5,
                    "code_generation": 8.5,
                    "code_debugging": 8.5,
                    "planning": 8.5,
                    "summarization": 8.0,
                    "quick_answer": 8.0,
                    "explanation": 8.5,
                    "long_form_writing": 8.5
                },
                "max_tokens": 262144,   # from official API
                "latency": 2.0,
                "cost": 1.4,            # $0.50/$1.50 per M tokens
                "stability": 8.5
            },
            "mistral-medium-2505": {
                "provider": MISTRAL,
                "model": "mistral-medium-2505",
                "tasks": {
                    "reasoning": 7.5,
                    "code_generation": 7.8,
                    "code_debugging": 7.8,
                    "planning": 7.5,
                    "summarization": 7.2,
                    "quick_answer": 7.2,
                    "explanation": 7.5,
                    "long_form_writing": 7.2
                },
                "max_tokens": 131072,   # from official API
                "latency": 1.0,
                "cost": 1.5,            # $0.40/$2.00 per M tokens
                "stability": 8.0        # original Medium 3, not the 2508 update
            },
            "open-mistral-nemo": {
                "provider": MISTRAL,
                "model": "open-mistral-nemo",
                "tasks": {
                    "reasoning": 5.8,
                    "code_generation": 6.0,
                    "code_debugging": 6.0,
                    "planning": 5.8,
                    "summarization": 6.2,
                    "quick_answer": 6.5,
                    "explanation": 6.0,
                    "long_form_writing": 5.8
                },
                "max_tokens": 131072,   # from official API
                "latency": 0.3,         # TTFT 0.33s, 154 t/s
                "cost": 0.3,            # $0.15/$0.15 per M tokens
                "stability": 7.5
            },
            "labs-leanstral-2603": {
                "provider": MISTRAL,
                "model": "labs-leanstral-2603",
                "tasks": {
                    "reasoning": 9.0,   # exceptional — formal proof reasoning
                    "code_generation": 8.5,
                    "code_debugging": 9.0,  # core strength: proof verification loop
                    "planning": 8.0,
                    "summarization": 6.0,   # not its primary use case
                    "quick_answer": 6.0,
                    "explanation": 7.5,
                    "long_form_writing": 6.5
                },
                "max_tokens": 196608,   # from official API
                "latency": 0.8,         # reasoning overhead on sparse MoE
                "cost": 0.0,            # free labs endpoint (limited time)
                "stability": 6.5        # experimental labs model
            },
            "ministral-3b-2512": {
                "provider": MISTRAL,
                "model": "ministral-3b-2512",
                "tasks": {
                    "reasoning": 5.0,
                    "code_generation": 5.0,
                    "code_debugging": 5.0,
                    "planning": 5.0,
                    "summarization": 5.8,
                    "quick_answer": 6.2,
                    "explanation": 5.5,
                    "long_form_writing": 5.0
                },
                "max_tokens": 131072,   # from official API — NOT 256000
                "latency": 0.2,         # TTFT 0.41s, 269 t/s — fastest Mistral model
                "cost": 0.2,            # $0.10/$0.10 per M tokens
                "stability": 7.5
            }
        }
    }
    return scores
