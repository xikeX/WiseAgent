"""
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 23:10:23
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 17:33:59
Description: The core of the agent. It is link the reporter, receiver, action
This file will be import in the sub module, so it should not import main module, or it will cause a circular import
"""

import importlib
from threading import Thread
from typing import Any, Callable, List

from numpy import single
from pydantic import BaseModel, Field

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG


@singleton
class AgentCore(BaseModel):
    action_manager: Any = []
    life_scheduler: dict[str, Any] = None
    receiver: Any = Field(default=None)
    monitor: Any = Field(default=None)
    agent_list: List[AgentData] = []

    # the agent will chose a life scheduler to start
    agent_life_threads: dict[str, Thread] = []

    start_function_list: List[Any] = []

    # a state to check the agent system is running
    _is_running: bool = True

    @property
    def is_running(self):
        # If the a
        if self._is_running is True:
            if not any([agent.is_alive for agent in self.agent_list]):
                self._is_running = False
        return self._is_running

    def _init_receiver(self):
        if GLOBAL_CONFIG.base_receiver_module_path is not None:
            receiver_module = importlib.import_module(GLOBAL_CONFIG.base_receiver_module_path)
            receiver_module.register(self)

    def _init_monitor(self):
        if GLOBAL_CONFIG.base_monitor_module_path is not None:
            receiver_module = importlib.import_module(GLOBAL_CONFIG.base_monitor_module_path)
            receiver_module.register(self)

    def start_pre_function(self):
        for function in self.start_function_list:
            function()

    def init_agent(self, agent_data: AgentData):
        """init the agent data."""

    def init_agent_data(self, agent_data: AgentData) -> bool:
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
            self.agent_life_threads[agent_data.name] = Thread(
                target=life_scheduler.start,
                args=(
                    self,
                    agent_data,
                ),
            )
            self.agent_life_threads[agent_data.name].start()

    def get_action(self, action_name: str = None):
        if action_name in self.action_manager:
            return self.action_manager[action_name]
        raise Exception(f"Action {action_name} not found")


def get_agent_core():
    return AgentCore()
