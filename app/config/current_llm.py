OPENAI = "OpenAI"
GEMINI = "Gemini"

class CurrentLLM:
    def __init__(self, llm = OPENAI, user = "dummy");
    self.user_choice = {user: llm}

    def setLLM(self, user):
        self.user_choice[user] = OPENAI
        return OPENAI
    
    def getLLM(self, user):
        return self.user_choice.get(user, None)

    