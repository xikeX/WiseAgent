"""
Author: Huang Weitao
Date: 2024-09-17 16:06:02
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:30:43
Description: 
"""

import os
from typing import List

import yaml
from pydantic import BaseModel

from wiseagent.common.yaml_config import YamlConfig
from wiseagent.config.const import CONFIG_PATH, ENV_CONFIG_PATH


class GlobalConfig(BaseModel, YamlConfig):
    # The reporter belong to the monitor
    reporter_module_path: List[str] = None

    # Life Scheduler(e.g. react, act ...) belong to the life manager
    life_scheduler_module_path: List[str] = None

    # Action belong to the action manager
    action_module_path: List[str] = None
    # Base Action class, which is used to select ActionClas from code file. e.g. ["BaseAtion", "BasePlanAction"]
    base_action_class: List[str] = None

    # LLM belong to the llm manager
    llm_module_path: List[str] = None

    env_yaml_path: str = None

    def __init__(self, **data):
        super().__init__(**data)
        self.env_yaml_path = self.env_yaml_path or ENV_CONFIG_PATH
        if self.env_yaml_path and os.path.exists(self.env_yaml_path):
            """load the env config from the env_yaml_path"""
            env_config = {}
            with open(self.env_yaml_path, "r", encoding="utf-8") as f:
                env_config = yaml.safe_load(f)
            type_map = {
                "type": "TYPE",
                "api_key": "API_KEY",
                "base_url": "BASE_URL",
                "model_name": "MODEL_NAME",
                "verbose": "VERBOSE",
            }
            if llm_config := env_config.get("LLM", None):
                for k, v in llm_config.items():
                    if k in type_map:
                        os.environ["LLM_" + type_map[k]] = str(v)
            if embedding_config := env_config.get("EMBEDDING", None):
                for k, v in embedding_config.items():
                    if k in type_map:
                        os.environ["EMBEDDING_" + type_map[k]] = v

    @classmethod
    def default(cls):
        config_file_path = CONFIG_PATH / "global_config.yaml"
        return cls.from_yaml_file(config_file_path)

    def add_reporter_module_path(self, module_path: str):
        self.reporter_module_path.append(module_path)

    def add_life_scheduler_module_path(self, module_path: str):
        self.life_scheduler_module_path.append(module_path)

    def add_action_module_path(self, module_path: str):
        self.action_module_path.append(module_path)
