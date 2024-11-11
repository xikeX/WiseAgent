"""
Author: Huang Weitao
Date: 2024-09-21 10:17:05
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 12:17:42
Description: 
"""
from typing import List

from wiseagent.action.base_action import BaseAction
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent


@singleton
class KnowledgeMemoryAction(BaseAction):
    action_description: str = "Actions to manage knowledge memory"

    # TODO:Some of this methods can be implemented in BaseAction

    def init_agent(self, agent_data: Agent):
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
