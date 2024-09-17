from wiseagent.receiver.perceptron import BasePerceptron
from wiseagent.agent_data.base_agent_data import BaseAgentData

class TextPerceptron(BasePerceptron):
    "The messsage of text. Usually in single agent system. And User is the sender"
    name: str = "TextPerceptron"
    cause_by: str = "Text"
    map_key_words: dict = {"Text"}
    
    async def handle_message(self, data: BaseAgentData,msg:BaseAgentData):
        # Add the received message to the short-term memory
        with data.short_term_memory_lock:
            data.short_term_memory.append(msg)
        
    