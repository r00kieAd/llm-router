import os
import requests
import traceback
from config.llm_config import LLMConfig
from config.current_llm import CurrentLLM
from fastapi.responses import JSONResponse

llm_obj = CurrentLLM()
config_obj = LLMConfig()

def updateUserLLM(user, llm):
    try:
        curr_llm = llm_obj.setLLM(user = user, choice = llm)
        config = config_obj.getUserConfig(user = user)
        return JSONResponse(status_code=200, content={"config_updated": True, "llm": curr_llm, "config": config})
    except Exception as e:
        # print(str(e))
        tb_frames = traceback.extract_tb(e.__traceback__) if hasattr(
            e, "__traceback__") and e.__traceback__ is not None else []
        line_number = tb_frames[-1].lineno if tb_frames else None
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "line_number": line_number
            }
        )


def updateSettings(user, temp, top_p, top_k, output_tokens, freq_penalty, presence_penalty):
    try:
        llm = llm_obj.getLLM(user)
        res = config_obj.setUserConfig(
            user = user,
            llm = llm,
            temp = temp,
            top_p = top_p,
            top_k = top_k,
            output_tokens = output_tokens,
            freq_penalty = freq_penalty,
            presence_penalty = presence_penalty)
        return JSONResponse(status_code=200, content={"config_updated": True, "result": res})
    except Exception as e:
        tb_frames = traceback.extract_tb(e.__traceback__) if hasattr(
            e, "__traceback__") and e.__traceback__ is not None else []
        line_number = tb_frames[-1].lineno if tb_frames else None
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "line_number": line_number
            }
        )
