'''
Author: Huang Weitao
Date: 2024-09-17 15:38:38
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 00:21:38
Description: 
'''

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from abc import ABC, abstractmethod

class BasePerceptron(BaseModel,ABC):
    "The Abstract Base Class for Perceptron"
    name:str = None
    cause_by: str = None
    map_key_words: dict = {}
    @abstractmethod
    def handle_message(self, data: AgentData,msg:AgentData):
        raise NotImplementedError("receiver method not implemented")
    
