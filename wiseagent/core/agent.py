"""
Author: Huang Weitao
Date: 2024-09-17 14:46:18
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 01:58:56
Description: Agent core data, contain all the necessary data for agent. Include the agent's property, action_list, report_config, etc.
"""

import threading
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import BaseModel

from wiseagent.common.const import WORKING_DIR
from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import (
    Message,
    SleepMessage,
    UserMessage,
    WakeupMessage,
)
from wiseagent.common.yaml_config import YamlConfig

# The current agent data.
# Do not modify __CURRENT_AGENT_DATA directly in other files, as it may cause unexpected errors.
# Use "with agent_data:" to switch this variable automatically.
CURRENT_AGENT_DATA = ContextVar("current_agent_data", default=None)


def get_current_agent_data():
    return CURRENT_AGENT_DATA.get()


AGENT_SYSTEM_PROMPT = """
You are a helpful agent and follow is the profile of you.

## name
{agent_name}

## description
{agent_description}

## Current Environment
{current_environment}
## Tools Description
{tools_description}

## Example
{agent_example}

## Instructions
{agent_instructions}

你的所有回答都必须遵循以上描述，且必须使用中文回答。
"""


class Agent(BaseModel, YamlConfig):
    agent_id: str = ""
    name: str
    description: str = ""
    # The agent's config file path
    config_file: str = ""

    model_config: dict = {"arbitrary_types_allowed": True}

    # Golbal System Prompt, This will be used in the agent's prompt.
    agent_system_prompt_template: str = AGENT_SYSTEM_PROMPT
    # The parameters in the agent_system_prompt_template
    current_environment: str = ""
    tools_description: str = ""
    agent_instructions: str = ""
    agent_example: str = ""

    # The working directory of the agent
    agent_global_working_dir: str = WORKING_DIR

    # The config of the agent
    action_list: List[str] = []
    action_data_config: dict = {}
    action_data: Dict[str, Any] = {}
    life_schedule_config: str = ""
    llm_config: Dict[str, str] = {"llm_type": None, "api_key": None}
    embedding_config: Dict[str, str] = {"llm_type": None, "api_key": None, "model_name": None, "base_url": None}

    # Control Sate
    _is_init: bool = False
    _is_alive: bool = False  # If is alive, the agent thread keep
    _is_activate: bool = False  # If is sleep, the agent will not act untill wake up
    wake_up_event: Any = None  # The event to wake up the agent

    # Memory
    short_term_memory: List = []
    short_term_memory_lock: Any = None
    new_observe_message_number: int = 0

    @classmethod
    def from_default(
        cls,
        name,
        description="",
        life_schedule_config="ReActLifeSchedule",
        default_plan="MethodPlanAction",
        action_list=["Chat"],
        **kwargs,
    ):
        kwargs["name"] = name
        kwargs["description"] = description
        kwargs["action_list"] = action_list or []
        if default_plan not in kwargs["action_list"]:
            kwargs["action_list"].append(default_plan)
        kwargs["life_schedule_config"] = life_schedule_config
        return cls(**kwargs)

    def after_init(self):
        """
        Initialize the agent after all configurations are set.
        This method sets up the lock for short-term memory.
        """
        self.short_term_memory_lock = threading.Lock()
        self.wake_up_event = threading.Event()

    def get_agent_system_prompt(
        self,
        name=None,
        description=None,
        current_environment=None,
        tools_description=None,
        agent_instructions=None,
        agent_example=None,
    ):
        """Set and Return the system prompt for the agent."""
        return self.agent_system_prompt_template.format(
            agent_name=name or self.name,
            agent_description=description or self.description,
            current_environment=current_environment or self.current_environment,
            tools_description=tools_description or self.tools_description,
            agent_instructions=agent_instructions or self.agent_instructions,
            agent_example=agent_example or self.agent_example,
        )

    def register_action(self, action):
        """
        Register an action to the agent.
        Args:
            action (BaseAction): The action to register.
        """
        from wiseagent.action.base_action import BaseAction

        if isinstance(action, BaseAction):
            self.action_list.append(action.action_name)
            action.init_agent(self)
            from wiseagent.core.agent_core import get_agent_core

            agent_core = get_agent_core()
            if agent_core._have_been_init is False:
                agent_core.init()
            agent_core.register(action)
        else:
            raise TypeError("Action must be an instance of BaseAction")

    def get_action_config(self, action_name):
        return self.action_data_config.get(action_name, None)

    def set_action_config(self, action_name, action_config):
        if action_name not in self.action_list:
            self.action_data_config[action_name] = action_config
        else:
            logger.info(f"Action {action_name} already registered, cannot set config.")

    def get_working_dir(self):
        return self.agent_global_working_dir

    def set_working_dir(self, path: Union[Path, str]):
        self.agent_global_working_dir = Path(path)

    def add_memory(self, message: Union[Message], from_env=False):
        """
        Args:
            message (Union[Message,str]): The message to add to the short term memory.
        """
        try:
            with self.short_term_memory_lock:
                logger.info(f"Add message to short term memory: {message}")
                self.short_term_memory.append(message)
                if from_env:
                    if self.is_activate is False:
                        self.wake_up()
                    self.new_observe_message_number += 1
        except Exception as e:
            logger.error(f"Error adding message to memory: {e}")

    def get_latest_memory(self, last_k: int = 30):
        return self.short_term_memory[-min(last_k, len(self.short_term_memory)) :]

    def set_short_term_memory(self, memory: List[Message]):
        with self.short_term_memory:
            self.short_term_memory = memory

    def observe(self, with_reset: bool = False):
        with self.short_term_memory_lock:
            res = self.new_observe_message_number
            if with_reset:
                self.new_observe_message_number = 0
        return res

    def set_action_data(self, action_name: str, data: Any):
        """
        This function is used to set the data of the action.
        """
        self.action_data[action_name] = data

    def get_action_data(self, action_name: str):
        if action_name in self.action_data:
            return self.action_data[action_name]
        else:
            raise ValueError(f"Action {action_name} not found in {self.__class__.__name__}")

    @property
    def is_init(self):
        return self._is_init

    @is_init.setter
    def is_init(self, value: bool):
        self._is_init = value

    @property
    def is_alive(self):
        """If the is_alive is False, the agent will stop sub threading and exit."""
        return self._is_alive

    @is_alive.setter
    def is_alive(self, value: bool):
        self._is_alive = value

    @property
    def is_activate(self):
        """If the is_activate is False, the agent will block."""
        return self._is_activate

    @is_activate.setter
    def is_activate(self, value: bool):
        self._is_activate = value

    def sleep(self):
        SleepMessage(send_from=self.name).send_message()
        self._is_activate = False

    def wake_up(self):
        WakeupMessage(send_from=self.name).send_message()
        self.wake_up_event.set()
        self._is_activate = True

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

    def life(self):
        """Start the agent's life cycle."""
        from wiseagent.core.agent_core import get_agent_core

        agent_core = get_agent_core()
        if agent_core._have_been_init is False:
            agent_core.init()
        if self.is_init is False:
            agent_core.init_agent(self)
        if self.is_alive is False:
            agent_core.start_agent_life(self)

    def ask(self, content):
        """
        This function is used to ask the agent a question.
        """
        if self.is_alive:
            message = UserMessage(content=content, send_from="user", send_to=self.name)
            self.add_memory(message, from_env=True)
        else:
            raise ValueError("Agent is not alive. Please use agent.life() to start the agent.")
