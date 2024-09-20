from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import AgentCore


class PlanAction(BaseModel, ABC):
    """Base class for all plan actions"""

    @abstractmethod
    def plan(self, agentData: "AgentData", **kwargs) -> Dict:
        """Execute the plan action
        Args:
            agentData (AgentData): The agent data, which include the hole information of the agent
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
