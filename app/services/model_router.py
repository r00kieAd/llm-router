from services.gemini_client import query_gemini
from services.openai_client import query_openai
from config.current_llm import CurrentLLM
from config.llm_config import LLMConfig
from config.all_models import model_provider
from services.prompt_preprocessing import preprocess_prompt
from services.task_inference import infer_task
from services.rank_models import select_model

config_obj = LLMConfig()
llm_obj = CurrentLLM()


def route_to_client(prompt: str, user: str, model: str, instruction: str) -> dict:
    client = llm_obj.getLLM(user)
    response = None
    preprocessed_dict = preprocess_prompt(prompt=prompt)
    task = infer_task(preprocessed=preprocessed_dict)
    task_ctx = {
        **task,
        "token_estimate": preprocessed_dict["token_estimate"]
    }
    result = select_model(task_ctx=task_ctx, provider_choice=client, model_choice=model)
    client = result.get("provider", None)
    model = result.get("model", None)
    if not model or model.lower() == model_provider("A").lower():
        response = "Could not select model. Try selecting manually"
        model = None
        return {
            "response": response or "No response returned",
            "provider": client or "Unknown",
            "model_used": model or "Unknown"
        }
    if client == model_provider("M1"):
        configs = get_configs(client, user)
        response = query_openai(prompt, model, instruction, temperature=configs.get("temp", 0), top_p=configs.get("top_p", 0), max_output_token=configs.get("max_out_tokens", 0))
    elif client == model_provider("M2"):
        configs = get_configs(client, user)
        response = query_gemini(prompt, model, instruction, temperature=configs.get("temp", 0), top_p=configs.get("top_p", 0), top_k=configs.get("top_k", 0), max_output_token=configs.get("max_out_tokens", 0))
    else:
        response = "Select a valid option"
        model = None
    return {
        "response": response or "No response returned",
        "provider": client or "Unknown",
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
