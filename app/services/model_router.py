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
    print(f'recevied_client: {client}, received_model: {model}, starting prompt preprocessing...')
    preprocessed_dict = preprocess_prompt(prompt=prompt)
    print('prompt preprocessing done, starting inference...')
    task = infer_task(preprocessed=preprocessed_dict)
    print('task inference done, starting model ranking...')
    client = select_model(task, client, model)
    print('model ranking done...returning response...')
    response = {
        "preprocess_results": preprocessed_dict,
        "task_inferred": task,
        "client": client
    }
    return {
        "response": response or "No response returned",
        "model_used": "Unknown"
    }
    match client:
        case model_provider("A"):
            response = "Auto Mode not ready yet. Try manually selecting the models"
            model = None
        case model_provider("M1"):
            if model.lower() == model_provider("A").lower():
                response = "Auto Mode not ready yet. Try manually selecting the models"
                model = None
            else:
                configs = get_configs(client, user)
                response = query_openai(prompt, model, instruction, temperature=configs.get("temp", 0), top_p=configs.get("top_p", 0), max_output_token=configs.get("max_out_tokens", 0))
        case model_provider("M2"):
            if model.lower() == model_provider("A").lower():
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
