
from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import BaseAgentData
from abc import ABC, abstractmethod
class BasePerceptron(BaseModel,ABC):
    "The Abstract Base Class for Perceptron"
    name:str = None
    cause_by: str = None
    map_key_words: dict = {}
    @abstractmethod
    async def handle_message(self, data: BaseAgentData,msg:BaseAgentData):
        raise NotImplementedError("receiver method not implemented")