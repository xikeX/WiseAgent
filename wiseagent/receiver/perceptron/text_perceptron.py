from wiseagent.common.annotation import singleton
from wiseagent.protocol.message import Message
from wiseagent.receiver.perceptron import BasePerceptron
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.config import logger

@singleton
class TextPerceptron(BasePerceptron):
    "The messsage of text. Usually in single agent system. And User is the sender"
    name: str = "TextPerceptron"
    cause_by: str = "Text"
    map_key_words: dict = {"Text"}
    
    def handle_message(self, data: AgentData,msg:Message):
        # Add the received message to the short-term memory
        with data.short_term_memory_lock:
            data.short_term_memory.append(msg)
            logger.info(f"TextPerceptron received message: {msg}")
        
def get_perceptron():
    return TextPerceptron()