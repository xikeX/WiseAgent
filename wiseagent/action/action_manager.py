"""
Author: Huang Weitao
Date: 2024-09-21 22:57:48
LastEditors: Huang Weitao
LastEditTime: 2024-09-22 15:46:32
Description: 
"""
import importlib
from typing import Any, Dict

from pydantic import BaseModel

from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG
from wiseagent.core.agent_core import AgentCore


@singleton
class ActionManager(BaseModel):
    action_map: Dict[str, Any] = {}

    def __init__(self) -> None:
        super().__init__()
        self.init_action()

    def init_action(self):
        for action_module_path in GLOBAL_CONFIG.action_module_path:
            action_module = importlib.import_module(action_module_path)
            action = action_module.get_action()
            if action.action_name not in self.action_map:
                self.action_map[action.action_name] = action

    def get_action(self, action_name: str):
        if action_name in self.action_map:
            return self.action_map[action_name]
        else:
            raise Exception(f"Action {action_name} not found")


def register(agent_core: "AgentCore"):
    agent_core.action_manager = ActionManager()
