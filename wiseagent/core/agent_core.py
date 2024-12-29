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

from wiseagent.common.global_config import GlobalConfig
from wiseagent.common.logs import logger
from wiseagent.common.singleton import singleton


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
    agent_manager: List[Any] = []

    # The workflow controller of the system
    # workflow_controller: Any = Field(default=None)
    _have_been_init: bool = False
    # The prepare function that must be call before the system ready.
    _prepare_function_list: List[Any] = []
    _close_function_list: List[Any] = []
    # When close the system, set the is_running to False, and the sub thread of the system will close.
    _is_running: bool = True
    global_config: Any = None

    @property
    def is_running(self):
        return self._is_running

    def __init__(self, config_file=None, global_config=None, **kwargs):
        super().__init__(**kwargs)
        if global_config is not None:
            self.global_config = global_config
        elif config_file is not None:
            from wiseagent.common.global_config import GlobalConfig

            self.global_config = GlobalConfig.from_yaml_file(config_file=config_file)
        else:
            from wiseagent.common.global_config import GlobalConfig

            self.global_config = GlobalConfig.default()

    def close(self):
        self._is_running = False
        self._have_been_init = False

    def init(self, global_config: GlobalConfig = None):
        """
        Init the agent system
        We Do not use the __init__ function, because it will be called in the sub module, and it will cause a circular import.
        """
        if self._have_been_init:
            return
        global_config = global_config or self.global_config
        self._init_receiver(global_config)
        self._init_monitor(global_config)
        self._init_life_manager(global_config)
        self._init_action_manager(global_config)
        self._init_llm_manager(global_config)
        self._preparetion()
        self._have_been_init = True

    def _init_receiver(self, global_config):
        from wiseagent.core.base_receiver import BaseReceiver

        self.receiver = BaseReceiver(global_config)
        self._prepare_function_list.append(self.receiver.run_receive_thread)
        self._close_function_list.append(self.receiver.close)

    def _init_monitor(self, global_config):
        from wiseagent.core.base_monitor import BaseMonitor

        self.monitor = BaseMonitor(global_config)
        self._prepare_function_list.append(self.monitor.run_report_thread)
        self._close_function_list.append(self.monitor.close)

    def _init_life_manager(self, global_config):
        from wiseagent.core.life_manager import LifeManager

        self.life_manager = LifeManager(global_config)

    def _init_action_manager(self, global_config):
        from wiseagent.action.action_manager import ActionManager

        self.action_manager = ActionManager(global_config)

    def _init_llm_manager(self, global_config):
        from wiseagent.core.llm_manager import LLMManager

        self.llm_manager = LLMManager(global_config)

    def register(self, obj):
        """
        Register Action, LLM, Monitor to the agent system
        """
        from wiseagent.action.base_action import BaseAction
        from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler
        from wiseagent.core.llm.base_llm import BaseLLM

        if isinstance(obj, BaseAction):
            if self.action_manager is None:
                raise Exception("Action manager is not init")
            self.action_manager.register(obj)
        elif isinstance(obj, BaseLLM):
            if self.llm_manager is None:
                raise Exception("LLM manager is not init")
            self.llm_manager.register(obj)
        elif isinstance(obj, BaseLifeScheduler):
            if self.life_manager is None:
                raise Exception("Life manager is not init")
            self.life_manager.register(obj)

    def _preparetion(self):
        """
        Pareparetion for the agent system. It will init the agent, and then start the agent system.
        In this function, the thread like receiver and reporter will be start.
        """
        for function in self._prepare_function_list:
            function()

    def init_agent(self, agent_data):
        """init the agent data. It will init the action data, get action description, add the agent to the agent list."""

        # Check the agent is init
        if agent_data.is_init is True:
            raise Exception("Agent is already init")

        # Check the agent name is unique
        if self.check_agent_exist(agent_data.name):
            raise Exception("Agent name is already exist. DO NOT use the same name for different agent")

        # Init the agent data to suit for the action. Add the tool description to agent.
        for action_item in agent_data.action_list:
            # action_class:method_name_1,method_name_2...
            action_class = action_item.split(":")[0]
            method_name_list = None
            if ":" in action_item:
                method_name_list = action_item.split(":")[1].split(",")
            action = self.get_action(action_class)
            action.init_agent(agent_data)
            tools_description = action.get_json_description(method_name_list)
            if tools_description:
                agent_data.tools_description += tools_description

        # Set the agent is init to True, and then the agent can be start.
        agent_data.is_init = True
        agent_data.after_init()

        # Add the agent to the agent list
        if agent_data not in self.agent_manager:
            self.agent_manager.append(agent_data)
        return agent_data

    def start_agent_life(self, agent_data, new_thread=True):
        if agent_data.is_init is False:
            raise Exception("Agent is not init")
        self.life_manager.life(agent_data, new_thread)
        logger.info(f"{agent_data.name}'s life start.")

    def get_action(self, action_name: str = None):
        return self.action_manager.get_action(action_name)

    def get_llm(self, llm_type: str = None):
        if self.llm_manager is None:
            logger.debug("llm manager is not init. init now...")
            self._init_llm_manager(self.global_config)
        return self.llm_manager.get_llm(llm_type)

    def check_agent_exist(self, agent_name: str):
        if any([agent_data.name == agent_name for agent_data in self.agent_manager]):
            return True
        return False

    def get_monitor(self):
        return self.monitor

    def get_receiver(self):
        return self.receiver

    def report_message(self, message: str):
        self.monitor.add_message(message)

    def remove_agent(self, agent_name):
        self.agent_list = [agent_data for agent_data in self.agent_list if agent_data.name != agent_name]


def get_agent_core():
    return AgentCore()
