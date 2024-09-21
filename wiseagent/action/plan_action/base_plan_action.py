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

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import AgentCore


class BasePlanAction(BaseModel, ABC):
    """Base class for all plan actions"""

    @abstractmethod
    def plan(self, **kwargs) -> Dict:
        """Execute the plan action
        Args:
            **kwargs: Additional arguments, which can be used by the plan action

        Returns:
            Dict: The result of the plan action, which may include thoughts, action command list, etc.
        """
        raise NotImplementedError("Subclass must implement abstract method")


def register(agent_core: "AgentCore"):
    """Register the plan action to the agent core.
    Usually it will include the action to the action_list.
    Args:
        agent_core (AgentCore): The agent core
    """
