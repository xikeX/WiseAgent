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

from pydantic import BaseModel, Field

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG


@singleton
class AgentCore(BaseModel):
    action_manager: Any = Field(default=None)
    life_manager: Any = Field(default=None)
    receiver: Any = Field(default=None)
    monitor: Any = Field(default=None)
    agent_list: List[AgentData] = []

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
            receiver_module.get_monitor(self)

    def _init_life_manager(self):
        if GLOBAL_CONFIG.life_manager_module_path is not None:
            life_scheduler_module = importlib.import_module(GLOBAL_CONFIG.life_manager_module_path)
            life_scheduler_module.register(self)

    def _init_action_manager(self):
        if GLOBAL_CONFIG.action_manager_module_path is not None:
            action_module = importlib.import_module(GLOBAL_CONFIG.action_manager_module_path)
            action_module.register(self)

    def preparetion(self):
        for function in self.start_function_list:
            function()

    def init_agent(self, agent_data: AgentData) -> AgentData:
        """init the agent data. It will init the action data, get action description, add the agent to the agent list."""
        if agent_data.is_init is True:
            raise Exception("Agent is already init")
        # Init the agent data to suit for the action
        for action_name in agent_data.action_ability:
            action = self.get_action(action_name)
            action.init(agent_data)
        # Get the action description to form the agent tools description
        agent_data.tools_description = ""
        for action_name in agent_data.action_ability:
            action = self.get_action(action_name)
            agent_data.tools_description += action.get_description()
        # Set the agent is init to True, and then the agent can be start.
        agent_data.is_init = True
        agent_data.after_init()
        # Add the agent to the agent list
        if agent_data not in self.agent_list:
            self.agent_list.append(agent_data)
        return agent_data

    def start_agent_life(self, agent_data: AgentData):
        if agent_data.is_init is False:
            raise Exception("Agent is not init")
        self.life_scheduler[agent_data.name].start()

    def get_action(self, action_name: str = None):
        if action_name in self.action_manager:
            return self.action_manager.get[action_name]
        raise Exception(f"Action {action_name} not found")


def get_agent_core():
    return AgentCore()
