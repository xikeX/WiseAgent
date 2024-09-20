"""
Author: Huang Weitao
Date: 2024-09-17 14:46:18
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 01:58:56
Description: Agent core data, contain all the necessary data for agent. Include the agent's property, action_ability, report_ability, etc.
"""

import threading
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union

from langchain.vectorstores import FAISS, Chroma
from pydantic import BaseModel, Field

from wiseagent.common.yaml_config import YamlConfig
from wiseagent.protocol.message import Message


class AgentData(BaseModel, YamlConfig):
    name: str
    data_save_file: str = ""
    action_ability: List[str] = []
    receive_ability: List[str] = []
    report_ability: List[str] = []
    life_schedule_ability: str = ""

    # memory
    short_term_memory: List = []
    # the memory windows, it means the number of memory that will add to the llm in short term memory.
    memory_windows: int = 100
    short_term_memory_lock: Any = None
    long_term_memory: Any = None
    long_term_memory_lock: Any = None
    knowledge_memory: Any = None
    knowledge_memory_lock: Any = None
    # the data use in action.
    _action_data: Dict[str, Any] = {}

    def __init__(self, **data):
        super().__init__(**data)
        # 在所有其他变量赋值完毕后初始化锁对象
        self.short_term_memory_lock = threading.Lock()
        self.long_term_memory_lock = threading.Lock()
        self.knowledge_memory_lock = threading.Lock()

    # state
    _is_alive: bool = True  # If is alive, the agent thread will keep
    _is_sleep: bool = False  # If is sleep, the agent will not act untill wake up
    # The interval of heartbeat, if the agent is sleep, the heartbeat will check the state if the agent is switched to wake up.
    heartbeat_interval: int = 1

    @property
    def is_alive(self):
        return self._is_alive

    @property
    def is_sleep(self):
        return not self._is_sleep

    def add_short_term_memory(self, message: Message):
        with self.short_term_memory_lock:
            self.short_term_memory.append(message)

    def set(self, key, value):
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
