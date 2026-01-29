from config.current_llm import CurrentLLM
from config.all_models import model_provider

OPENAI = model_provider("M1")
GEMINI = model_provider("M2")
LLM = 'llm'
TEMP = 'temp'
TOPP = 'top_p'
TOPK = 'top_k'
OUTTOKENS = 'output_tokens'
FREQ = 'freq_penalty'
PRESENCE = 'presence_penalty'


class LLMConfig:
    llm_settings = {}
    llm_obj = CurrentLLM()

    def setUserConfig(self, user, llm, temp = None, top_p = None, top_k = None, output_tokens = None, freq_penalty = None, presence_penalty = None):
        if not self.__class__.llm_settings.get(user, None):
            self.__class__.llm_settings[user] = {}
        self.__class__.llm_settings[user][llm] = {
            TEMP: self.getDefaultTemp() if not temp else temp,
            TOPP: self.getDefaultTop_p() if not top_p else top_p,
            TOPK: self.getDefaultTop_k((OPENAI if not llm else llm), user) if not top_k else top_k,
            OUTTOKENS: self.getDefaultMaxOutputTokens() if not output_tokens else output_tokens,
            FREQ: self.getDefaultFreqPenalty() if not freq_penalty else freq_penalty,
            PRESENCE: self.getDefaultPresencePenalty() if not presence_penalty else presence_penalty
        }
        return self.__class__.llm_settings[user][llm]
    
    def getUserConfig(self, user):
        if not user:
            return None
        llm = self.__class__.llm_obj.getLLM(user)
        if not self.__class__.llm_settings.get(user, None) or not self.__class__.llm_settings[user].get(llm, None):
            return self.setUserConfig(user = user, llm = llm)
        return self.__class__.llm_settings[user][llm]
    
    def delUserConfig(self, user):
        del self.__class__.llm_settings[user]
        return

    def getDefaultTemp(self):
        return 0.7

    def getDefaultTop_p(self):
        return 1.0

    def getDefaultTop_k(self, llm, user):
        if llm == OPENAI and self.__class__.llm_obj.getLLM(user) == OPENAI:
            return 3
        elif llm == GEMINI and self.__class__.llm_obj.getLLM(user) == GEMINI:
            return 40
        else:
            return 1

    def getDefaultMaxOutputTokens(self):
        return 1024

    def getDefaultFreqPenalty(self):
        return 0.0

    def getDefaultPresencePenalty(self):
        return 0.0

    def userExists(self, user):
        return self.__class__.llm_settings.get(user, 0) == 0

    def llmAccess(self, user, llm):
        return self.__class__.llm_settings[user].get(llm, 0) == 0

    def setTemperature(self, llm, user, temp=None):
        if temp is None:
            temp = self.getDefaultTemp()
        self.__class__.llm_settings[user][llm][TEMP] = temp
        return self.__class__.llm_settings[user][llm][TEMP]

    def getTemperature(self, llm, user):
        if self.userExists(user):
            return self.setTemperature(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTemperature(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][TEMP]

    def setTopP(self, llm, user, top_p=None):
        if top_p is None:
            top_p = self.getDefaultTop_p()
        self.__class__.llm_settings[user][llm][TOPP] = top_p
        return self.__class__.llm_settings[user][llm][TOPP]

    def getTopP(self, llm, user):
        if self.userExists(user):
            return self.setTopP(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTopP(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][TOPP]

    def setTopK(self, llm, user, top_k=None):
        if top_k is None:
            top_k = self.getDefaultTop_k(llm, user)
        self.__class__.llm_settings[user][llm][TOPK] = top_k
        return self.__class__.llm_settings[user][llm][TOPK]

    def getTopK(self, llm, user):
        if self.userExists(user):
            return self.setTopK(llm, user)
        elif self.llmAccess(user, llm):
            return self.setTopK(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][TOPK]

    def setMaxOutputTokens(self, llm, user, output_tokens=None):
        if output_tokens is None:
            output_tokens = self.getDefaultMaxOutputTokens()
        self.__class__.llm_settings[user][llm][OUTTOKENS] = output_tokens
        return self.__class__.llm_settings[user][llm][OUTTOKENS]

    def getMaxOutputTokens(self, llm, user):
        if self.userExists(user):
            return self.setMaxOutputTokens(llm, user)
        elif self.llmAccess(user, llm):
            return self.setMaxOutputTokens(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][OUTTOKENS]

    def setFreqPenalty(self, llm, user, freq_penalty=None):
        if freq_penalty is None:
            freq_penalty = self.getDefaultFreqPenalty()
        self.__class__.llm_settings[user][llm][FREQ] = freq_penalty
        return self.__class__.llm_settings[user][llm][FREQ]

    def getFreqPenalty(self, llm, user):
        if self.userExists(user):
            return self.setFreqPenalty(llm, user)
        elif self.llmAccess(user, llm):
            return self.setFreqPenalty(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][FREQ]

    def setPresencePenalty(self, llm, user, presence_penalty=None):
        if presence_penalty is None:
            presence_penalty = self.getDefaultPresencePenalty()
        self.__class__.llm_settings[user][llm][PRESENCE] = presence_penalty
        return self.__class__.llm_settings[user][llm][PRESENCE]

    def getPresencePenalty(self, llm, user):
        if self.userExists(user):
            return self.setPresencePenalty(llm, user)
        elif self.llmAccess(user, llm):
            return self.setPresencePenalty(llm, user)
        else:
            return self.__class__.llm_settings[user][llm][PRESENCE]
