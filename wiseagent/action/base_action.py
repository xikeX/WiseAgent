"""
Author: Huang Weitao
Date: 2024-09-17 14:23:53
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 14:46:02
Description: 
"""

import json
from typing import List

import multidict
from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.common.get_action_class_descirption import get_action_class_desciprtion
from wiseagent.core.agent_core import AgentCore
from wiseagent.protocol.action_command import ActionCommand


@singleton
class BaseAction(BaseModel):
    action_name: str = ""
    action_type: str = ""
    action_description: str = ""

    def __init__(self):
        # Get the desciprtion of the class
        self.action_description = get_action_class_desciprtion(self)

    def get_json_description(self):
        res = json.dumps(self.action_description, ensure_ascii=False, indent=4)
        return res

    def get_xml_description(self):
        res = multidict.unparse(self.action_description, pretty=True)
        return res

    def init_agent(self):
        """Add special action data to the agent to enable it to perform specific actions. Default will do nothing."""

    def check_start(self, command_list: List[ActionCommand] = None):
        """
        Check whether the action should be initiated and modify the command list accordingly.
        By default, this function does nothing.

        Args:
            agent_data (AgentData): The data object for the agent.
            command_list (List[str]): The list of commands to be checked and potentially modified.
        """

    def llm_ask(sel, command_list: List[ActionCommand] = None):
        """
        Ask the LLM to perform the action and modify the command list accordingly.
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
