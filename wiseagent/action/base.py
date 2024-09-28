"""
Author: Huang Weitao
Date: 2024-09-17 14:23:53
LastEditors: Huang Weitao
LastEditTime: 2024-09-23 21:55:50
Description: 
"""

import json
from copy import deepcopy
from typing import Dict, List

import multidict
from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.common.get_action_class_descirption import get_action_class_desciprtion
from wiseagent.core.agent_core import AgentCore, get_agent_core
from wiseagent.protocol.action_command import ActionCommand
from wiseagent.protocol.message import Message


class BaseAction(BaseModel):
    action_name: str = ""  # the action name is the same with the action class
    action_type: str = ""
    action_description: str = None

    def __init__(self):
        super().__init__()
        # Get the desciprtion of the class
        self.action_description = get_action_class_desciprtion(self.__class__)
        self.action_name = self.__class__.__name__

    def _description_filter(self, action_config):
        if self.action_description is None:
            self.action_description = get_action_class_desciprtion(self)
        sub_description = deepcopy(self.action_description)
        if action_config:
            if "method" in action_config:
                sub_description["method"] = {}
                for method_name in action_config["method"]:
                    sub_description["method"][method_name] = self.action_description["method"][method_name]
        return sub_description

    def get_json_description(self, action_config=None):
        description = self._description_filter(action_config)
        res = json.dumps(description, ensure_ascii=False, indent=4)
        return res

    def get_xml_description(self, action_config=None):
        description = self._description_filter(action_config)
        res = multidict.unparse(description, pretty=True)
        return res

    def init_agent(self, agent_data: "AgentData"):
        """Add special action data to the agent to enable it to perform specific actions. Default will do nothing."""

    def check_start(self, command_list: List[ActionCommand] = None):
        """
        Check whether the action should be initiated and modify the command list accordingly.
        By default, this function does nothing.

        Args:
            agent_data (AgentData): The data object for the agent.
            command_list (List[str]): The list of commands to be checked and potentially modified.
        """

    def llm_ask(self, prompt, memory: List[Message] = None, system_prompt: str = None):
        """Ask the LLM to generate a response to the given prompt."""
        agent_data: AgentData = get_current_agent_data()
        agent_core = get_agent_core()
        if memory is None:
            # Get the lastest memory from the agent autumaticly
            memory = agent_data.get_last_memory()
        memory = memory + [Message(role="user", content=prompt)]
        llm = agent_core.get_llm(agent_data.llm_ability["llm_name"])
        if not llm:
            raise Exception("LLM not found")
        if not llm.check() and agent_data.llm_ability["api_key"]:
            llm.set_api_key(agent_data.llm_ability["api_key"])
        rsp = llm.llm_ask(memory=memory, system_prompt=system_prompt)
        return rsp


class BaseActionData(BaseModel):
    meta_data: Dict[str, str] = []

    def __init__(self):
        super().__init__()
        if self.meta_data is None:
            self.meta_data = {"class_name": self.__class__.__name__, "module_name": self.__class__.__module__}
            self.meta_data.update({"module_json", self.model_dump()})


def get_action() -> BaseAction:
    raise NotImplementedError("BaseAction can not be get")
