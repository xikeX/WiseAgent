"""
Author: Huang Weitao
Date: 2024-09-21 19:19:27
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 22:52:53
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-17 14:46:18
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 01:58:56
Description: Agent core data, contain all the necessary data for agent. Include the agent's property, action_ability, report_ability, etc.
"""

import threading
from contextvars import ContextVar
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union
from venv import logger

# from langchain.vectorstores import FAISS, Chroma
from pydantic import BaseModel, Field

from wiseagent.agent_data.base_agent_data_prompt import AGENT_SYSTEM_PROMPT
from wiseagent.common.yaml_config import YamlConfig
from wiseagent.protocol.message import Message

# The current agent data.
# Do not modify __CURRENT_AGENT_DATA directly in other files, as it may cause unexpected errors.
# Use "with agent_data:" to switch this variable automatically.
__CURRENT_AGENT_DATA = ContextVar("current_agent_data", default=None)


def get_current_agent_data():
    return __CURRENT_AGENT_DATA.get()


class AgentData(BaseModel, YamlConfig):
    name: str
    description: str = ""
    data_save_file: str = ""

    # Personal Prompt
    agent_system_prompt: str = AGENT_SYSTEM_PROMPT
    tools_description: str = ""  # This will be initialize in the agent_core.init_agent
    agent_instructions: str = ""
    agent_example: str = ""

    # This will be set to ture in the agent_core.init_agent to prevent the agent not initialized or  being initialized multiple times
    is_init: bool = False

    # The ability of the agent
    action_ability: List[str] = []
    receive_ability: List[str] = []
    report_ability: List[str] = []
    life_schedule_ability: str = ""

    # Memory
    short_term_memory: List = []
    new_message_number: int = 0  # If new message come, this will be add 1. after get message, this will be reset to 0.
    memory_windows: int = (
        100  # The memory windows, it means the number of memory that will add to the llm in short term memory.
    )
    short_term_memory_lock: Any = None
    long_term_memory: Any = None
    long_term_memory_lock: Any = None
    knowledge_memory: Any = None
    knowledge_memory_lock: Any = None

    # The data use in action. It is comment to create a data class for each action
    _action_data: Dict[str, Any] = {}

    # state
    _is_alive: bool = True  # If is alive, the agent thread will keep
    _is_sleep: bool = False  # If is sleep, the agent will not act untill wake up
    # The interval of heartbeat, if the agent is sleep, the heartbeat will check the state if the agent is switched to wake up.
    heartbeat_interval: int = 1

    def after_init(self):
        # After all is init, the agent can be format the main prompt
        self.agent_system_prompt = self.agent_system_prompt.format(
            name=self.name,
            description=self.description,
            tools_description=self.tools_description,
            agent_instructions=self.agent_instructions,
            agent_example=self.agent_example,
        )

    @property
    def is_alive(self):
        """If the is_alive is False, the agent will stop sub threading and exit."""
        return self._is_alive

    @property
    def is_sleep(self):
        """If the is_sleep is False, the action will stop take action but keep the thread."""
        return not self._is_sleep

    def add_memory(self, message: Message):
        """
        NOTE:
            There has two way to implement this function.
            One is implement in here (agent_data). It is convenient for receiver to add short term memory.
            Another is implement in short term memory manager action. It is convenient for manager memory.
            I chose the first one, but I will implement the second one in the future.
        # TODO: add_memory implement in short term memory manager action
        """
        with self.short_term_memory_lock:
            self.short_term_memory.append(message)
            self.new_message_number += 1

    def get_new_memory(self):
        """Get new message from short term memory."""
        new_message = None
        if self.new_message_number > 0:
            with self.short_term_memory_lock:
                new_message = self.short_term_memory[-self.new_message_number :]
                self.new_message_number = 0
        return new_message

    def observe(self):
        with self.new_message_number:
            self.new_message_number = 0

    def set_attribute(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise ValueError(f"Key {key} not found in {self.__class__.__name__}")

    def set_action_data(self, action_name: str, data: Dict[str, Any]):
        """
        # TODO: Note: This function may cause serialization issues if the data contains non-serializable objects.
        """
        self._action_data[action_name] = data

    def get_action_data(self, action_name: str):
        if action_name in self._action_data:
            return self._action_data[action_name]
        else:
            raise ValueError(f"Action {action_name} not found in {self.__class__.__name__}")

    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise ValueError(f"Key {key} not found in {self.__class__.__name__}")

    def __enter__(self):
        current_agent_data = __CURRENT_AGENT_DATA.set(self)
        logger.debug(f"__CURRENT_AGENT_DATA: Set to {self.name}.")
        if current_agent_data is not None:
            raise ValueError("current_agent_data is already set")

    def __exit__(self):
        current_agent_data = __CURRENT_AGENT_DATA.set(None)
        logger.debug("__CURRENT_AGENT_DATA: Release")
        if current_agent_data != self:
            raise ValueError("current_agent_data is not set to self")
