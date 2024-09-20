"""
Author: Huang Weitao
Date: 2024-09-17 16:06:02
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 22:54:09
Description: 
"""

from typing import List

from pydantic import BaseModel

from wiseagent.common.yaml_config import YamlConfig
from wiseagent.config import CONFIG_PATH


class GlobalConfig(BaseModel, YamlConfig):
    perceptron_module_path: List[str] = None
    base_receiver_module_path: str = ""

    reporter_module_path: List[str] = None
    base_monitor_module_path: str = ""

    @classmethod
    def default(cls):
        config_file_path = CONFIG_PATH / "global_config.yaml"
        return cls.from_yaml_file(config_file_path)

    def update(self, key, value, mode="append"):
        if hasattr(self, key):
            if mode == "append":
                setattr(self, key, getattr(self, key) + value)
            elif mode == "overwrite":
                setattr(self, key, value)
            elif mode == "create":
                raise ValueError("key exist. If you want to overwrite it, use mode = overwrite")
        else:
            if mode == "create":
                setattr(self, key, value)
            else:
                raise ValueError("key not exist")


# TODO: use customer file path to update global config
GLOBAL_CONFIG = GlobalConfig.default()
