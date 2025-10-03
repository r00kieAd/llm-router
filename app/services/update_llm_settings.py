
import os, requests, traceback
from config.llm_config import LLMConfig
from config.curr_llm import CurrentLLM
from fastapi.responses import JSONResponse

def updateUserLLM(user):
    return CurrentLLM.setLLM(user)

def updateSettings(user, temp, top_p, top_k, output_tokens, freq_penalty, presence_penalty):
    res = LLMConfig.setUserConfig(user, temp, top_p, top_k, output_tokens, freq_penalty, presence_penalty)
    return res
