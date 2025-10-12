OPENAI = "OpenAI"
GEMINI = "Gemini"

class CurrentLLM:
    user_choice = {}

    def setLLM(self, user, choice = OPENAI):
        self.__class__.user_choice[user] = choice
        return self.__class__.user_choice[user]
    
    def getLLM(self, user):
        return self.__class__.user_choice.get(user, None)
    
    def removeLLM(self, user):
        if self.getLLM(user) is not None:
            del self.__class__.user_choice[user]
        return True

    