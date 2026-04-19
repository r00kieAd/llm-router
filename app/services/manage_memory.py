from collections import deque

class Memory:
    def __init__(self):
        self.two_turn_memory = {}

    def add_new_prompt(self, prompt: str = "", username: str = ""):
        try:
            if not username:
                return False, prompt
            
            if self.two_turn_memory.get(username, None) is None:
                self.two_turn_memory[username] = deque(maxlen=2)

            self.two_turn_memory[username].append({"prompt": prompt, "res": ""})

            history = self.two_turn_memory[username]
            parts = []

            for turn in history:
                parts.append(f"User: {turn['prompt']}")
                if turn["res"]:
                    parts.append(f"Assistant: {turn['res']}")
            context = "\n".join(parts)
            return True, context
        except Exception as e:
            print(e)
            return False, prompt
    
    def add_new_response(self, res: list[str], username: str = ""):
        try:
            if not username or self.two_turn_memory.get(username, None) is None:
                return False, "no user found"
            
            if not res:
                return False, "no res found, no memory update"
            
            res = "".join(res)
            res = res[:500] + "..." if len(res) > 500 else res

            self.two_turn_memory[username][-1]["res"] = res

            # print(f"updated memory: {self.two_turn_memory[username]}")
            return True, "memory updated"
        except Exception as e:
            print(e)
            return False, "memory not updated"
    
    def clear_memory(self, username: str = ""):
        try:
            if not username:
                return False, 'no user found'
            
            del self.two_turn_memory[username]
            return True, 'memory cleared'
        except Exception as e:
            return False, "unknown error occured"

mem_instance = Memory()