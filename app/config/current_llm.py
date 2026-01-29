from config.all_models import model_provider

AUTO = model_provider("A")
OPENAI = model_provider("M1")
GEMINI = model_provider("M2")

class CurrentLLM:
    user_choice = {}

    def setLLM(self, user, choice = AUTO):
        self.__class__.user_choice[user] = choice
        return self.__class__.user_choice[user]
    
    def getLLM(self, user):
        return self.__class__.user_choice.get(user, None)
    
    def removeLLM(self, user):
        if self.getLLM(user) is not None:
            del self.__class__.user_choice[user]
        return True

    