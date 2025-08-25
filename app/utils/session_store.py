import os

class Tokens:
    def __init__(self):
        self.active_tokens: dict = {}
        self.token_count: int = 0
    
    def increaseCount(self):
        self.token_count += 1

    def decreaseCount(self):
        self.token_count -= 1
    
    def getTokenCount(self):
        return self.token_count

    def validToken(self, username, token):
        try:
            if self.active_tokens.get(username, 0) != 0:               
                return self.active_tokens[username] == token
            return False
        except:
            return False
    
    def addToken(self, username, token):
        try:
            if self.active_tokens.get(username, 0) == 0:
                self.increaseCount()
            self.active_tokens[username] = token
            print(self.active_tokens)
            return True
        except:
            self.decreaseCount()
            return False
    
    def deleteToken(self, username):
        try:
            print(self.active_tokens)
            if self.active_tokens.get(username, 0) == 0:
                return True
            del self.active_tokens[username]
            print(self.active_tokens)
            self.decreaseCount()
            return True
        except:
            return False

token_store = Tokens()    
