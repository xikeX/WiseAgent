"""
Author: Huang Weitao
Date: 2024-09-21 02:48:15
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:33:03
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-17 14:22:59
LastEditors: Huang Weitao
LastEditTime:  2024-09-22 11:31:59
Description: The core of the agent. It is link the reporter, receiver, action
This file will be import in the sub module, so it should not import main module, or it will cause a circular import
"""

import importlib
from typing import Any, List

from pydantic import BaseModel, Field

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG


@singleton
class AgentCore(BaseModel):
    # the manager of the Action(e.g. chat, arxiv, wechat_acton, ...)
    action_manager: Any = Field(default=None)
    life_manager: Any = Field(default=None)
    llm_manager: Any = Field(default=None)

    # The interface to receive the message from the outside world
    receiver: Any = Field(default=None)
    monitor: Any = Field(default=None)

    # The agent list in current system
    agent_list: List[AgentData] = []

    # The workflow controller of the system
    # workflow_controller: Any = Field(default=None)
    _have_been_init: bool = False
    # The prepare function that must be call before the system ready.
    _prepare_function_list: List[Any] = []
    _close_function_list: List[Any] = []
    # When close the system, set the is_running to False, and the sub thread of the system will close.
    _is_running: bool = True

    @property
    def is_running(self):
        return self._is_running

    def close(self):
        self._is_running = False

    def init(self):
        """
        Init the agent system
        We Do not use the __init__ function, because it will be called in the sub module, and it will cause a circular import.
        """
        if self._have_been_init:
            return

        self._init_receiver()
        self._init_monitor()
        self._init_life_manager()
        self._init_action_manager()
        self._init_llm_manager()
        self._preparetion()
        self._have_been_init = True

    def _init_receiver(self):
        if GLOBAL_CONFIG.base_receiver_module_path is not None:
            receiver_module = importlib.import_module(GLOBAL_CONFIG.base_receiver_module_path)
            receiver_module.register(self)

    def _init_monitor(self):
        if GLOBAL_CONFIG.base_monitor_module_path is not None:
            receiver_module = importlib.import_module(GLOBAL_CONFIG.base_monitor_module_path)
            receiver_module.register(self)

    def _init_life_manager(self):
        if GLOBAL_CONFIG.life_manager_module_path is not None:
            life_scheduler_module = importlib.import_module(GLOBAL_CONFIG.life_manager_module_path)
            life_scheduler_module.register(self)

    def _init_action_manager(self):
        if GLOBAL_CONFIG.action_manager_module_path is not None:
            action_module = importlib.import_module(GLOBAL_CONFIG.action_manager_module_path)
            action_module.register(self)

    def _init_llm_manager(self):
        if GLOBAL_CONFIG.llm_manager_module_path is not None:
            llm_module = importlib.import_module(GLOBAL_CONFIG.llm_manager_module_path)
            llm_module.register(self)

    def _preparetion(self):
        """
        Pareparetion for the agent system. It will init the agent, and then start the agent system.
        In this function, the thread like receiver and reporter will be start.
        """
        for function in self._prepare_function_list:
            function()

    def init_agent(self, agent_data: AgentData) -> AgentData:
        """init the agent data. It will init the action data, get action description, add the agent to the agent list."""

        # Check the agent is init
        if agent_data.is_init is True:
            raise Exception("Agent is already init")

        # Check the agent name is unique
        if self.check_agent_exist(agent_data.name):
            raise Exception("Agent name is already exist. DO NOT use the same name for different agent")

        # Init the agent data to suit for the action
        for action_config in agent_data.action_ability:
            action_name = action_config["action_name"]
            action = self.get_action(action_name)
            action.init_agent(agent_data)

        # Get the action description to form the agent tools description
        agent_data.tools_description = ""
        for action_config in agent_data.action_ability:
            action_name = action_config["action_name"]
            action = self.get_action(action_name)
            tools_description = action.get_json_description(action_config)
            if tools_description:
                agent_data.tools_description += tools_description

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
        self.life_manager.life(agent_data)

    def get_action(self, action_name: str = None):
        return self.action_manager.get_action(action_name)

    def get_llm(self, llm_name: str = None):
        return self.llm_manager.get_llm(llm_name)

    def check_agent_exist(self, agent_name: str):
        if any([agent_data.name == agent_name for agent_data in self.agent_list]):
            return True
        return False

    def get_monitor(self):
        return self.monitor

    def get_receiver(self):
        return self.receiver


def get_agent_core():
    return AgentCore()
