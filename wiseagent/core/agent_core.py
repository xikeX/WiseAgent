'''
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 23:59:02
Description: 
'''
'''
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 17:33:59
Description: The core of the agent. It is link the reporter, receiver, action
'''

from threading import Thread
from typing import Callable, ClassVar, List
from numpy import single
from pydantic import BaseModel
import importlib

from wiseagent.action.base_action import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.core.life_scheduler.base_life_scheduler import LifeScheduler
from wiseagent.config import GLOBAL_CONFIG

@singleton
class AgentCore(BaseModel):
    class Config:
        arbitrary_types_allowed=True
    action_list:List[BaseAction] = []
    # monitor:Monitor = None
    life_scheduler:dict[str,LifeScheduler] = None
    receiver: = None
    agent_list:List[AgentData] = []
    
    # the agent will chose a life scheduler to start
    agent_life_threads:dict[str,Thread] = []
    
    start_function_list: List[Callable[["AgentCore"], None]] = []
    
    # a state to check the agent system is running
    _is_running:bool = True
    
    @property
    def is_running(self):
        # If the a
        if self._is_running is True:
            if not any([agent.is_alive for agent in self.agent_list]):
                self._is_running = False
        return self._is_running
    
    def _init_receiver(self):
        if GLOBAL_CONFIG.base_receiver_model_path is not None:
            receiver_module = importlib.import_module(GLOBAL_CONFIG.base_receiver_model_path)
            receiver_module.register(self)
            
    def start_pre_function(self):
        for function in self.start_function_list:
            function(self)
    
    def init_agent(self, agent_data:AgentData):
        """init the agent data."""
        
    def init_agent_data(self, agent_data:AgentData) -> bool:
        # TODO: init the agent data
        if agent_data not in self.agent_list:
            self.agent_list.append(agent_data)
            return True
        return False
    
    def start_agent_life(self):
        for agent_data in self.agent_list:
            if self.agent_life_threads.get(agent_data.name) is not None:
                continue
            life_scheduler = self.life_scheduler.get(agent_data.life_scheduler)
            self.agent_life_threads[agent_data.name] = Thread(target=life_scheduler.start, args=(self,agent_data,))
            self.agent_life_threads[agent_data.name].start()
            
def get_agent_core():
    return AgentCore()