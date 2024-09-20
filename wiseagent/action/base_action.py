"""
Author: Huang Weitao
Date: 2024-09-17 14:23:53
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 14:46:02
Description: 
"""

from typing import List

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import AgentCore
from wiseagent.protocol.action_command import ActionCommand


@singleton
class BaseAction(BaseModel):
    action_name: str = ""
    action_type: str = ""
    action_description: str = ""

    def init_agent(self, agent_data: "AgentData"):
        """Add special action data to the agent to enable it to perform specific actions. Default will do nothing."""

    def check_start(self, agent_data: "AgentData", command_list: List[ActionCommand]):
        """
        Check whether the action should be initiated and modify the command list accordingly.
        By default, this function does nothing.

        Args:
            agent_data (AgentData): The data object for the agent.
            command_list (List[str]): The list of commands to be checked and potentially modified.
        """


def base_register(agent_core: "AgentCore"):
    """Register the action to the agent core.
    This make a example of how to register an action to the agent core.
    Args:
        agent_core (AgentCore): The agent core
    """
    agent_core.action_list.append(BaseAction())


def resgiter(agent_core: AgentCore):
    """Register the action to the agent core.
    This make a example of how to register an action to the agent core.
    Args:
        agent_core (AgentCore): The agent core
    """
