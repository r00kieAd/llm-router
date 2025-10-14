from services.gemini_client import query_gemini
from services.openai_client import query_openai
from config.current_llm import CurrentLLM
from config.llm_config import LLMConfig

OPENAI = "OpenAI"
GEMINI = "Gemini"

config_obj = LLMConfig()
llm_obj = CurrentLLM()

def route_to_client(prompt: str, user: str, model: str, instruction: str) -> dict:
    client = llm_obj.getLLM(user)
    temp = config_obj.getTemperature(llm = client, user = user)
    top_p = config_obj.getTopP(llm = client, user = user)
    top_k = config_obj.getTopK(llm = client, user = user)
    max_out_tokens = config_obj.getMaxOutputTokens(llm = client, user = user)
    # freq_penalty = config_obj.getFreqPenalty(llm = client, user = user)
    # presence_penalty = config_obj.getPresencePenalty(llm = client, user = user)
    if client == GEMINI:
        response = query_gemini(prompt, model, instruction, temperature = temp, top_p = top_p, top_k = top_k, max_output_token = max_out_tokens)
    elif client == OPENAI:
        response = query_openai(prompt, model, instruction, temperature = temp, top_p = top_p, max_output_token = max_out_tokens)
    else:
        response = "Select a valid client"
        model = None

    return {
        "response": response or "No response returned",
        "model_used": model or "Unknown"
    }