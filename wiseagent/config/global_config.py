"""
Author: Huang Weitao
Date: 2024-09-17 16:06:02
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:30:43
Description: 
"""

from typing import List

from pydantic import BaseModel

from wiseagent.common.annotation import singleton
from wiseagent.common.yaml_config import YamlConfig
from wiseagent.config import CONFIG_PATH


class GlobalConfig(BaseModel, YamlConfig):
    # The perceptron belong to the receiver
    perceptron_module_path: List[str] = None
    base_receiver_module_path: str = ""  # the base path of the receiver

    # The reporter belong to the monitor
    reporter_module_path: List[str] = None
    base_monitor_module_path: str = ""  # the base path of the monitor

    # Life Scheduler(e.g. react, act ...) belong to the life manager
    life_scheduler_module_path: List[str] = None
    life_manager_module_path: str = ""

    # Action belong to the action manager
    action_module_path: List[str] = None
    action_manager_module_path: str = ""

    # LLM belong to the llm manager
    llm_module_path: List[str] = None
    llm_manager_module_path: str = ""

    @classmethod
    def default(cls):
        config_file_path = CONFIG_PATH / "global_config.yaml"
        return cls.from_yaml_file(config_file_path)

    def add_perceptron_module_path(self, module_path: str):
        self.perceptron_module_path.append(module_path)

    def add_reporter_module_path(self, module_path: str):
        self.reporter_module_path.append(module_path)

    def add_life_scheduler_module_path(self, module_path: str):
        self.life_scheduler_module_path.append(module_path)

    def add_action_module_path(self, module_path: str):
        self.action_module_path.append(module_path)


# TODO: use customer file path to update global config
GLOBAL_CONFIG = GlobalConfig.default()
