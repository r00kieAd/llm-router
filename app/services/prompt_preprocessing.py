import re

def normalize_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    prompt = re.sub(r"\s+", " ", prompt)
    return prompt

# def detect_language(prompt: str) -> str:
#     ascii_ratio = sum(c.isascii() for c in prompt) / max(len(prompt), 1)
#     return "en" if ascii_ratio > 0.9 else "non_en"

def estimate_tokens(prompt: str) -> int:
    return int(len(prompt.split()) * 1.3)

def extract_signals(prompt: str) -> dict:
    lower = prompt.lower()
    return {
        "has_code": any(k in prompt for k in ["```", "def ", "class ", "import ", "{", "}"]),
        "has_math": any(k in prompt for k in ["=", "+", "-", "*", "/", "^"]),
        "has_list": any(k in prompt for k in ["1.", "2.", "-", "*"]),
        "has_question": "?" in prompt,
        "has_constraints": any(k in lower for k in ["must", "should", "only", "exactly"]),
        "has_examples": "example" in lower or "e.g." in lower,
        "has_system_style": any(k in lower for k in ["you are", "act as", "behave like"]),
    }

def extract_intent_cues(prompt: str) -> dict:
    lower = prompt.lower()
    return {
        "mentions_write": "write" in lower,
        "mentions_explain": "explain" in lower or "why" in lower,
        "mentions_fix": "fix" in lower or "debug" in lower,
        "mentions_optimize": "optimize" in lower or "improve" in lower,
        "mentions_summarize": "summarize" in lower or "tl;dr" in lower,
    }

def preprocess_prompt(prompt: str) -> dict:
    normalized = normalize_prompt(prompt)
    return {
        "prompt": normalized,
        "token_estimate": estimate_tokens(normalized),
        "length_chars": len(normalized),
        "signals": extract_signals(normalized),
        "intent_cues": extract_intent_cues(normalized),
        "is_short": len(normalized) < 200,
        "is_long": len(normalized) > 2000,
    }