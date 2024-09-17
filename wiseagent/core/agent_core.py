'''
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 17:50:22
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
from typing import Callable, List
from pydantic import BaseModel
import importlib

from wiseagent.action.base_action import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.receiver.base_receiver import BaseReceiver
from wiseagent.config import global_config

class AgentCore(BaseModel):
    action_list:List[BaseAction] = []
    monitor:Monitor = None
    life_scheduler:dict[str,LifeScheduler] = None
    receiver:BaseReceiver = None
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if global_config.base_receiver_model_path is not None:
            receiver_module = importlib.import_module(global_config.base_receiver_model_path).BaseReceiver()
            receiver_module.register(self)
            
    def start_function(self):
        for function in self.start_function_list:
            function(self)
    
    def init_agent(self, agent_data:AgentData):
        """init the agent data."""
        
        
    
    def start_agent_life(self):
        for agent_data in self.agent_list:
            if self.agent_life_threads.get(agent_data.name) is not None:
                continue
            life_scheduler = self.life_scheduler.get(agent_data.life_scheduler)
            self.agent_life_threads[agent_data.name] = Thread(target=life_scheduler.start, args=(self,agent_data,))
            self.agent_life_threads[agent_data.name].start()
            
            
            