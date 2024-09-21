"""
Author: Huang Weitao
Date: 2024-09-21 10:19:36
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 12:17:16
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-21 10:19:36
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 10:40:06
Description: 
"""
from abc import ABC, abstractmethod
from typing import List

from wiseagent.action.base_action import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.protocol.action_command import ActionCommand


class BaseMemoryAction(BaseAction, ABC):
    action_name: str = "BaseMemoryAction"
    action_type: str = "MemoryAtion"

    # TODO:Some of this methods can be implemented in BaseAction

    @abstractmethod
    def init_agent(self, agent_data: AgentData):
        pass

    @abstractmethod
    def check_start(self, command_list: List[ActionCommand] = None):  # type: ignore
        pass

    @abstractmethod
    def get_memory_store(self, **kwargs):
        pass

    @abstractmethod
    def clear_memory(self, oldest_k: int = 10):
        pass

    @abstractmethod
    def get_memory(self, memory_id):
        pass

    @abstractmethod
    def get_memory_list_by_query(self, query):
        pass

    @abstractmethod
    def get_memory_list(self, last_k: int = 10):
        pass

    @abstractmethod
    def add_memory(self, memory):
        pass
