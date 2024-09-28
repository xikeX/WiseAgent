"""
Author: Huang Weitao
Date: 2024-09-21 02:48:15
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 11:08:47
Description: 
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel

from wiseagent.action.base import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import AgentCore


class BasePlanAction(BaseAction, ABC):
    """Base class for all plan actions"""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def plan(self, **kwargs) -> Dict:
        """Execute the plan action
        Args:
            **kwargs: Additional arguments, which can be used by the plan action

        Returns:
            Dict: The result of the plan action, which may include thoughts, action command list, etc.
        """
        raise NotImplementedError("Subclass must implement abstract method")


def get_action():
    raise NotImplementedError("BasePlanAction is an abstract class and cannot be instantiated")
