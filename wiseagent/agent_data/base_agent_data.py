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

# from langchain.vectorstores import FAISS, Chroma
from pydantic import BaseModel, Field

from wiseagent.agent_data.base_agent_data_prompt import AGENT_SYSTEM_PROMPT
from wiseagent.common.yaml_config import YamlConfig
from wiseagent.config import logger
from wiseagent.config.const import WORKING_DIR
from wiseagent.protocol.message import Message, SleepMessage, WakeupMessage

# The current agent data.
# Do not modify __CURRENT_AGENT_DATA directly in other files, as it may cause unexpected errors.
# Use "with agent_data:" to switch this variable automatically.
CURRENT_AGENT_DATA = ContextVar("current_agent_data", default=None)


def get_current_agent_data():
    return CURRENT_AGENT_DATA.get()


class AgentData(BaseModel, YamlConfig):
    name: str
    description: str = ""
    data_save_file: str = ""

    # Personal Prompt. This exmaple will add into the system prompt of the agent
    agent_system_prompt_template: str = AGENT_SYSTEM_PROMPT
    agent_system_prompt: str = ""
    current_environment: str = ""
    tools_description: str = ""  # This will be initialize in the agent_core.init_agent
    agent_instructions: str = ""
    agent_example: str = ""

    action_experience: dict = {}  #

    __agent_global_working_dir: str = WORKING_DIR

    # This will be set to ture in the agent_core.init_agent to prevent the agent not initialized or  being initialized multiple times
    is_init: bool = False

    # The ability of the agent
    action_ability: List[Dict[str, str]] = []
    receive_ability: List[str] = []
    report_ability: List[str] = []
    life_schedule_ability: str = ""
    llm_ability: Dict[str, str] = {"llm_name": None, "api_key": None}

    # Memory
    short_term_memory: List = []
    uncheck_message_number: int = (
        0  # If new message come, this will be add 1. after get message, this will be reset to 0.
    )
    memory_windows: int = (
        100  # The memory windows, it means the number of memory that will add to the llm in short term memory.
    )
    short_term_memory_lock: Any = []
    long_term_memory: Any = None
    long_term_memory_lock: Any = None
    knowledge_memory: Any = None
    knowledge_memory_lock: Any = None
    current_knowledge: str = None  # This will be assinged in "action" annotation to get the useful knowledge for the action for knowledge memory

    # The data use in action. It is comment to create a data class for each action
    _action_data: Dict[str, Any] = {}

    # state
    _is_alive: bool = True  # If is alive, the agent thread will keep
    _is_sleep: bool = True  # If is sleep, the agent will not act untill wake up
    # The interval of heartbeat, if the agent is sleep, the heartbeat will check the state if the agent is switched to wake up.
    heartbeat_interval: int = 1

    # The other agent in the same network. {"name":"agent_description"}
    other_agent: Dict[str, str] = []

    def after_init(self):
        # After all is init, the agent can be format the main prompt
        self.long_term_memory_lock = threading.Lock()
        self.short_term_memory_lock = threading.Lock()
        self.knowledge_memory_lock = threading.Lock()
        self.agent_system_prompt = self.get_agent_system_prompt()

    def get_agent_system_prompt(
        self,
        name=None,
        description=None,
        current_environment=None,
        tools_description=None,
        agent_instructions=None,
        agent_example=None,
    ):
        name = name or self.name
        description = description or self.description
        current_environment = current_environment or self.current_environment
        tools_description = tools_description or self.tools_description
        agent_instructions = agent_instructions or self.agent_instructions
        agent_example = agent_example or self.agent_example
        system_prompt = self.agent_system_prompt_template.format(
            agent_name=name,
            agent_description=description,
            current_environment=current_environment,
            tools_description=tools_description,
            agent_instructions=agent_instructions,
            agent_example=agent_example,
        )
        return system_prompt

    def get_experience(self, action_name):
        return self.action_experience.get(action_name, None)

    def get_working_dir(self):
        return self.__agent_global_working_dir

    def set_working_dir(self, path: Union[Path, str]):
        self.__agent_global_working_dir = Path(path)

    @property
    def is_alive(self):
        """If the is_alive is False, the agent will stop sub threading and exit."""
        return self._is_alive

    @property
    def is_sleep(self):
        """If the is_sleep is False, the action will stop take action but keep the thread."""
        return self._is_sleep

    def sleep(self):
        from wiseagent.core.agent_core import get_agent_core

        monitor = get_agent_core().get_monitor()
        monitor.add_message(SleepMessage(send_from=self.name))
        self._is_sleep = True

    def wake_up(self):
        from wiseagent.core.agent_core import get_agent_core

        monitor = get_agent_core().get_monitor()
        monitor.add_message(WakeupMessage(send_from=self.name))
        self._is_sleep = False

    def add_memory(self, message: Union[Message], from_env=False):
        """
        Args:
            message (Union[Message,str]): The message to add to the short term memory.
        NOTE:
            There has two way to implement this function.
            One is implement in here (agent_data). It is convenient for receiver to add short term memory.
            Another is implement in short term memory manager action. It is convenient for manager memory.
            I chose the first one, but I will implement the second one in the future.
        # TODO: add_memory implement in short term memory manager action
        """
        # When add Memory, the message will change to Normal Message.
        message.track.append(f"file:{__file__} function:add_memory")
        with self.short_term_memory_lock:
            logger.info(f"Add message to short term memory: {message}")
            self.short_term_memory.append(message)
            if from_env:
                self.uncheck_message_number += 1

    def get_last_memory(self, last_k: int = 10):
        return self.short_term_memory[-last_k:]

    def observe(self, with_reset: bool = False):
        with self.short_term_memory_lock:
            res = self.uncheck_message_number
            if with_reset:
                self.uncheck_message_number = 0
        return res

    def set_action_data(self, action_name: str, data: Any):
        """
        # TODO: Note: This function may cause serialization issues if the data contains non-serializable objects.
        """
        self._action_data[action_name] = data

    def get_action_data(self, action_name: str):
        if action_name in self._action_data:
            return self._action_data[action_name]
        else:
            raise ValueError(f"Action {action_name} not found in {self.__class__.__name__}")

    def set_action_knowledge(self, knowledge: str):
        self.current_knowledge = knowledge

    def get_action_knowledge(self):
        return self.current_knowledge

    def __enter__(self):
        global CURRENT_AGENT_DATA
        current_agent_data = CURRENT_AGENT_DATA.get()
        if current_agent_data is not None:
            raise ValueError("current_agent_data is already set")
        CURRENT_AGENT_DATA.set(self)
        logger.debug(f"__CURRENT_AGENT_DATA: Set to {self.name}.")

    def __exit__(self, exc_type, exc_value, traceback):
        global CURRENT_AGENT_DATA
        current_agent_data = CURRENT_AGENT_DATA.get()
        if current_agent_data != self:
            raise ValueError("current_agent_data is not set to self")
        CURRENT_AGENT_DATA.set(None)
        logger.debug("__CURRENT_AGENT_DATA: Release")
