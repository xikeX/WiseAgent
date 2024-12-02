"""
Author: Huang Weitao
Date: 2024-09-21 22:57:48
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 20:04:13
Description: 
"""
import importlib
import os
import re
import time
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel

from wiseagent.action.base_action import BaseAction
from wiseagent.common.global_config import GlobalConfig
from wiseagent.common.logs import logger
from wiseagent.common.singleton import singleton
from wiseagent.common.utils import listdir

PACKAGE_NAME = "wiseagent.action."


@singleton
class ActionManager(BaseModel):
    action_map: Dict[str, Any] = {}
    exclude_module_list: list = []
    action_module_path_map: Dict[str, Any] = {}
    base_action_class: list[str] = []

    def __init__(self, global_config: GlobalConfig):
        super().__init__()
        start_time = time.time()
        self.init_action(global_config)
        end_time = time.time()
        logger.info(f"ActionManager init time: {end_time - start_time} s")

    def init_action(self, global_config: GlobalConfig):
        action_module_path_list = global_config.action_module_path
        if "base_action_class" in global_config:
            self.base_action_class = global_config.base_action_class
        if "BaseAction" not in self.base_action_class:
            self.base_action_class.append("BaseAction")
        if "BasePlanAction" not in self.base_action_class:
            self.base_action_class.append("BasePlanAction")
        if "default" in global_config.action_module_path:
            # When 'default' is in action_module_path, it means to load all action modules in the action folder
            action_module_folder = Path(__file__).parent
            action_module_path_list = [
                module_path for module_path in action_module_path_list if module_path != "default"
            ]
            for module_path, deepth in listdir(
                folder=action_module_folder, deepth=0, filter=lambda x: x.suffix == ".py"
            ):
                if deepth == 0 or any(exclude in str(module_path) for exclude in self.exclude_module_list):
                    continue
                module = PACKAGE_NAME + ".".join(str(module_path)[:-3].split("\\")[-deepth - 1 :])
                action_module_path_list.append(module)
            action_module_path_list = list(set(action_module_path_list))
        for action_module_path in action_module_path_list:
            package_spec = importlib.util.find_spec(action_module_path)
            if package_spec is None or package_spec.origin is None:
                logger.info(f"Action {action_module_path} not found")
                continue
            action_names = self.get_action_name_from_file(package_spec.origin)
            for action_name in action_names:
                self.action_module_path_map[action_name] = action_module_path

    def get_action_name_from_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            pattern = re.compile(r"class\s+(\w+)\s*\(([^)]*)\):", re.DOTALL)
            matches = pattern.findall(content)
        return [match[0] for match in matches if any(base_action in match[1] for base_action in self.base_action_class)]

    def get_action(self, action_name: str):
        if action_name in self.action_map:
            return self.action_map[action_name]
        elif action_name in self.action_module_path_map:
            action_module_path = self.action_module_path_map[action_name]
            action_module = importlib.import_module(action_module_path)
            if hasattr(action_module, action_name):
                self.action_map[action_name] = getattr(action_module, action_name)()
            return self.action_map[action_name]
        else:
            raise Exception(f"Action {action_name} not found")

    def register(self, action: BaseAction = None, action_module_path: str = None):
        if action is None and action_module_path is None:
            raise Exception("Action or action_module_path must be provided")
        if isinstance(action, BaseAction):
            self.action_map[action.action_name] = action
        elif isinstance(action_module_path, str):
            get_action_name_from_file = self.get_action_name_from_file(action_module_path)
            if len(get_action_name_from_file) == 0:
                logger.info(f"No action found in {action_module_path}")
                return
            for action_name in get_action_name_from_file:
                self.action_module_path_map[action_name] = action_module_path
        else:
            raise Exception("Invalid argument type")
