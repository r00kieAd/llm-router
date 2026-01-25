from services.gemini_client import query_gemini
from services.openai_client import query_openai
from config.current_llm import CurrentLLM
from config.llm_config import LLMConfig
from services.prompt_preprocessing import preprocess_prompt

AUTO = "Auto".lower()
OPENAI = "OpenAI"
GEMINI = "Gemini"

config_obj = LLMConfig()
llm_obj = CurrentLLM()


def route_to_client(prompt: str, user: str, model: str, instruction: str) -> dict:
    # response = preprocess_prompt(prompt=prompt)
    client = llm_obj.getLLM(user)
    response = None
    match client:
        case "Auto":
            response = "Auto Mode not ready yet. Try manually selecting the models"
            model = None
        case "OpenAI":
            # print(f'in OpenAI scope: {client}')
            if model.lower() == AUTO:
                response = "Auto Mode not ready yet. Try manually selecting the models"
                model = None
            else:
                configs = get_configs(client, user)
                response = query_openai(prompt, model, instruction, temperature=configs.get("temp", 0), top_p=configs.get("top_p", 0), max_output_token=configs.get("max_out_tokens", 0))
        case "Gemini":
            # print(f'in Gemini scope: {client}')
            if model.lower() == AUTO:
                response = "Auto Mode not ready yet. Try manually selecting the models"
                model = None
            else:
                configs = get_configs(client, user)
                response = query_gemini(prompt, model, instruction, temperature=configs.get("temp", 0), top_p=configs.get("top_p", 0), top_k=configs.get("top_k", 0), max_output_token=configs.get("max_out_tokens", 0))
        case _:
            response = "Select a valid client"
            model = None
    return {
        "response": response or "No response returned",
        "model_used": model or "Unknown"
    }


def get_configs(client, user):
    return {
        "temp": config_obj.getTemperature(llm=client, user=user),
        "top_p": config_obj.getTopP(llm=client, user=user),
        "top_k": config_obj.getTopK(llm=client, user=user),
        "max_out_tokens": config_obj.getMaxOutputTokens(llm=client, user=user)
        # "freq_penalty": config_obj.getFreqPenalty(llm = client, user = user)
        # "presence_penalty": config_obj.getPresencePenalty(llm = client, user = user)
    }
