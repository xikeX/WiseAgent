import importlib
from typing import Dict

from wiseagent.action.base_action import BaseAction
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG
from wiseagent.core.agent_core import AgentCore


@singleton
class ActionManager:
    action_map: Dict[str, BaseAction] = {}

    def __init__(self) -> None:
        self.init_action()

    def init_action(self, action: BaseAction):
        for action_module_path in GLOBAL_CONFIG.action_module_path:
            action_module = importlib.import_module(action_module_path)
            action = action_module.get_action()
            if action.name not in self.action_map:
                self.action_map[action.name] = action

    def get_action(self, action_name: str):
        if action_name in self.action_map:
            return self.action_map[action_name]
        else:
            raise Exception(f"Action {action_name} not found")


def resgiter(agent_core: "AgentCore"):
    agent_core.action_manager = ActionManager()
