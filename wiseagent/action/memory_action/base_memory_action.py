"""
Author: Huang Weitao
Date: 2024-09-21 10:19:36
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 12:17:16
Description: 
"""
from typing import List

from wiseagent.action.base import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.protocol.action_command import ActionCommand


class BaseMemoryAction(BaseAction):
    action_type: str = "MemoryAtion"

    # TODO:Some of this methods can be implemented in BaseAction

    def init_agent(self, agent_data: AgentData):
        pass

    def check_start(self, command_list: List[ActionCommand] = None):  # type: ignore
        pass

    def get_memory_store(self, **kwargs):
        pass

    def clear_memory(self, oldest_k: int = 10):
        pass

    def get_memory(self, memory_id):
        pass

    def get_memory_list_by_query(self, query):
        pass

    def get_memory_list(self, last_k: int = 10):
        pass

    def add_memory(self, memory):
        pass


def get_action():
    raise NotImplementedError("BaseMemoryAction is an abstract class")
