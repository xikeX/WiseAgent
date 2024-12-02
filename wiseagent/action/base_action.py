"""
Author: Huang Weitao
Date: 2024-09-17 14:23:53
LastEditors: Huang Weitao
LastEditTime: 2024-09-23 21:55:50
Description: 
"""

import json
from abc import abstractmethod
from copy import deepcopy
from typing import Dict, List

import multidict
from pydantic import BaseModel

from wiseagent.action.action_annotation import get_dict_description
from wiseagent.common.logs import logger
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.protocol_message import Message, UserMessage
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.core.agent_core import get_agent_core


class BaseAction(BaseModel):
    action_name: str = ""  # the action name is the same with the action class
    action_type: str = ""
    action_description: str = None

    def __init__(self):
        super().__init__()
        # Get the desciprtion of the class
        self.action_name = self.__class__.__name__
        self.action_description = get_dict_description(self.__class__)

    def set_action_data(self, agent_data, action_data):
        """Set the action data
        Args:
            agent_data (AgentData): the agent data
            action_data (BaseActionData): the action data"""
        agent_data.set_action_type(self.action_name, action_data)

    def get_action_data(self, return_agent_data=False, action_name=None):
        """Return the current action data. If return_agent_data is True, also return the agent data"""
        agent_data = get_current_agent_data()
        action_data = agent_data.get_action_data(action_name or self.action_name) if agent_data else None
        if return_agent_data:
            return action_data, agent_data
        return action_data

    def _description_filter(self, method_name_list):
        """Get the description of the action method"""
        sub_description = deepcopy(self.action_description)
        if method_name_list:
            sub_description["method"] = {}
            for method_name in sub_description:
                if method_name in self.action_description["method"]:
                    sub_description["method"][method_name] = self.action_description["method"][method_name]
                else:
                    logger.warning(f"Method {method_name} not found in action {self.action_name}")
        return sub_description

    def get_json_description(self, action_config=None):
        description = self._description_filter(action_config)
        res = json.dumps(description, ensure_ascii=False, indent=4)
        return res

    def get_xml_description(self, action_config=None):
        description = self._description_filter(action_config)
        res = multidict.unparse(description, pretty=True)
        return res

    def init_agent(self, agent_data: "Agent"):
        """Add special action data to the agent to enable it to perform specific actions. Default will do nothing."""

    def check_start(self, command_list: List[ActionCommand] = None):
        """
        Check whether the action should be initiated and modify the command list accordingly.
        By default, this function does nothing.

        Args:
            agent_data (AgentData): The data object for the agent.
            command_list (List[str]): The list of commands to be checked and potentially modified.
        """

    def llm_ask(self, prompt, memory: List[Message] = None, system_prompt: str = None, handle_stream_function=None):
        """Ask the LLM to generate a response to the given prompt."""
        agent_data: Agent = get_current_agent_data()
        agent_core = get_agent_core()
        if memory is None:
            # Get the lastest memory from the agent autumaticly
            memory = agent_data.get_latest_memory()
        memory = memory + [UserMessage(content=prompt)]
        llm = agent_core.get_llm(agent_data.llm_config["llm_type"])
        if not llm:
            raise Exception("LLM not found")
        rsp = llm.llm_ask(
            memory=memory,
            system_prompt=system_prompt,
            handle_stream_function=handle_stream_function,
            base_url=agent_data.llm_config.get("base_url", None),
            api_key=agent_data.llm_config.get("api_key", None),
            model_name=agent_data.llm_config.get("model_name", None),
        )
        return rsp


class BasePlanAction(BaseAction):
    @abstractmethod
    def plan(self, command_list: List[ActionCommand]) -> Dict:
        raise NotImplementedError("BaseActionData can not be plan")


class BaseActionData(BaseModel):
    meta_data: Dict[str, str] = []

    def __init__(self):
        super().__init__()
        if self.meta_data is None:
            self.meta_data = {"class_name": self.__class__.__name__, "module_name": self.__class__.__module__}
            self.meta_data.update({"module_json", self.model_dump()})
