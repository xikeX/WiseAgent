'''
Author: Huang Weitao
Date: 2024-09-17 14:46:18
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 23:13:09
Description: 
'''
'''
Author: Huang Weitao
Date: 2024-09-17 14:46:18
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 15:06:56
Description: Agent core data, contain all the necessary data for agent. Include the agent's property, action_ability, report_ability, etc.
'''

from pathlib import Path
import threading
from typing import ClassVar, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from langchain.vectorstores import Chroma, FAISS
from wiseagent.common.yaml_config import YamlConfig

class AgentData(BaseModel,YamlConfig):
    class Config:
        arbitrary_types_allowed = True
    name: str
    data_save_file: str
    property: dict
    action_ability: dict
    receive_ability: list[str] = []
    report_ability: dict
    life_schedule_ability: str
    
    # memory
    short_term_memory: List = []
    short_term_memory_lock:ClassVar[threading.Lock] = threading.Lock()
    long_term_memory: Union[Chroma,FAISS] = None
    long_term_memory_lock:ClassVar[threading.Lock] = threading.Lock()
    knowledge_memory: Union[Chroma,FAISS] = None
    knowledge_memory_lock:ClassVar[threading.Lock] = threading.Lock()
    
    # state
    _is_alive: bool = True
    @property
    def is_alive(self):
        return self._is_alive 
    def set(self,key,value):
        if hasattr(self,key):
            setattr(self,key,value)
        else:
            raise ValueError(f"Key {key} not found in {self.__class__.__name__}")
    
    def get(self,key):
        if hasattr(self,key):
            return getattr(self,key)
        else:
            raise ValueError(f"Key {key} not found in {self.__class__.__name__}")
        
