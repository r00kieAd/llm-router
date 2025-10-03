from config.current_llm import CurrentLLM


OPENAI = "OpenAI"
GEMINI = "Gemini"
LLM = 'llm'
TEMP = 'temp'
TOPP = 'top_p'
TOPK = 'top_k'
OUTTOKENS = 'output_tokens'
FREQ = 'freq_penalty'
PRESENCE = 'presence_penalty'


class LLMConfig:
    def __init__(self):
        self.llm_settings = {}

    def setUserConfig(self, user, llm = NONE, temp = None, top_p = None, top_k = None, output_tokens = None, freq_penalty = None, presence_penalty = None):
        llm = CurrentLLM.getLLM(user)
        self.llm_settings[user][llm] = {
            TEMP: getDefaultTemp() if not temp else temp,
            TOPP: getDefaultTop_p() if not top_p else top_p,
            TOPK: getDefaultTop_k(OPENAI if not llm else llm, user) if not top_k else top_k,
            OUTTOKENS: getDefaultMaxOutputTokens() if not output_tokens else output_tokens,
            FREQ: getDefaultFreqPenalty() if not freq_penalty else freq_penalty,
            PRESENCE: getDefaultPresencePenalty() if not presence_penalty else presence_penalty
        }
        return self.llm_settings[user][llm]
    
    def getUserConfig(self, user, llm):
        if not user or not llm:
            return
        return self.llm_settings[user][llm]
    
    def delUserConfig(self, user):
        del self.llm_settings[user]
        return

    def getDefaultTemp(self):
        return 1.0

    def getDefaultTop_p(self):
        return 1.0

    def getDefaultTop_k(self, llm, user):
        if llm == OPENAI and CurrentLLM.getLLM(user) == OPENAI:
            return 3
        elif llm == GEMINI and CurrentLLM.getLLM(user) == GEMINI:
            return 40
        else:
            return 1

    def getDefaultMaxOutputTokens(self):
        return 8000

    def getDefaultFreqPenalty(self):
        return 0.0

    def getDefaultPresencePenalty(self):
        return 0.0

    def userExists(self, user):
        return self.llm_settings.get(user, 0) == 0

    def llmAccess(self, user, llm):
        return self.llm_settings[user].get(llm, 0) == 0

    def setTemperature(self, llm, user, temp=None):
        if temp is None:
            temp = self.getDefaultTemp()
        self.llm_settings[user][llm][TEMP] = temp
        return self.llm_settings[user][llm][TEMP]

    def getTemperature(self, llm, user):
        if self.userExists(user):
            return self.setTemperature(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTemperature(llm, user)
        else:
            return self.llm_settings[user][llm][TEMP]

    def setTopP(self, llm, user, top_p=None):
        if top_p is None:
            top_p = self.getDefaultTop_p()
        self.llm_settings[user][llm][TOPP] = top_p
        return self.llm_settings[user][llm][TOPP]

    def getTopP(self, llm, user):
        if self.userExists(user):
            return self.setTopP(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTopP(llm, user)
        else:
            return self.llm_settings[user][llm][TOPP]

    def setTopK(self, llm, user, top_k=None):
        if top_k is None:
            top_k = self.getDefaultTop_k(llm, user)
        self.llm_settings[user][llm][TOPK] = top_k
        return self.llm_settings[user][llm][TOPK]

    def getTopK(self, llm, user):
        if self.userExists(user):
            return self.setTopK(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTopK(llm, user)
        else:
            return self.llm_settings[user][llm][TOPK]

    def setMaxOutputTokens(self, llm, user, output_tokens=None):
        if output_tokens is None:
            output_tokens = self.getDefaultMaxOutputTokens()
        self.llm_settings[user][llm][OUTTOKENS] = output_tokens
        return self.llm_settings[user][llm][OUTTOKENS]

    def getMaxOutputTokens(self, llm, user):
        if self.userExists(user):
            return self.setMaxOutputTokens(llm, user)
        elif self.llmAccess(user, llm):
            return self.setMaxOutputTokens(llm, user)
        else:
            return self.llm_settings[user][llm][OUTTOKENS]

    def setFreqPenalty(self, llm, user, freq_penalty=None):
        if freq_penalty is None:
            freq_penalty = self.getDefaultFreqPenalty()
        self.llm_settings[user][llm][FREQ] = freq_penalty
        return self.llm_settings[user][llm][FREQ]

    def getFreqPenalty(self, llm, user):
        if self.userExists(user):
            return self.setFreqPenalty(llm, user)
        elif self.llmAccess(user, llm):
            return self.setFreqPenalty(llm, user)
        else:
            return self.llm_settings[user][llm][FREQ]

    def setPresencePenalty(self, llm, user, presence_penalty=None):
        if presence_penalty is None:
            presence_penalty = self.getDefaultPresencePenalty()
        self.llm_settings[user][llm][PRESENCE] = presence_penalty
        return self.llm_settings[user][llm][PRESENCE]

    def getPresencePenalty(self, llm, user):
        if self.userExists(user):
            return self.setPresencePenalty(llm, user)
        elif self.llmAccess(user, llm):
            return self.setPresencePenalty(llm, user)
        else:
            return self.llm_settings[user][llm][PRESENCE]
