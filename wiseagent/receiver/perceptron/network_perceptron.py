from wiseagent.common.annotation import singleton
from wiseagent.receiver.perceptron import BasePerceptron
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.message import Message
from wiseagent.config import logger
@singleton
class NetworkPerceptron(BasePerceptron):
    "The messsage of text. Usually in single multi-agent system. And the sender is other Agent."
    name: str = "NetworkPerceptron"
    cause_by: str = "Network"
    map_key_words: dict = {"Network"}
    
    async def handle_message(self, data: AgentData,msg:Message):
        # Add the received message to the short-term memory
        with data.short_term_memory_lock:
            data.short_term_memory.append(msg)
            logger.info(f"NetworkPerceptron received message: {msg}")
        
def get_perceptron():
    return NetworkPerceptron()