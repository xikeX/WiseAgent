from wiseagent.receiver.perceptron import BasePerceptron
from wiseagent.agent_data.base_agent_data import BaseAgentData

class NetworkPerceptron(BasePerceptron):
    "The messsage of text. Usually in single multi-agent system. And the sender is other Agent."
    name: str = "NetworkPerceptron"
    cause_by: str = "Network"
    map_key_words: dict = {"Network"}
    
    async def handle_message(self, data: BaseAgentData,msg:BaseAgentData):
        # Add the received message to the short-term memory
        with data.short_term_memory_lock:
            data.short_term_memory.append(msg)
        
    