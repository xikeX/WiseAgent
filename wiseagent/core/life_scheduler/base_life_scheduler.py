"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 00:25:11
Description: 
"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from wiseagent.common.protocol_message import Message, UserMessage
from wiseagent.core.agent import Agent, get_current_agent_data


class BaseLifeScheduler(BaseModel, ABC):
    """Base class for all life schedules"""

    name: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.__class__.__name__

    @abstractmethod
    def life(self):
        pass

    def llm_ask(self, prompt, memory: List[Message] = None, system_prompt: str = None, handle_stream_function=None):
        """Ask the LLM to generate a response to the given prompt."""
        agent_data: Agent = get_current_agent_data()
        from wiseagent.core.agent_core import get_agent_core

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
            temperature=agent_data.llm_config.get("temperature", None),
        )
        return rsp

    def get_agent_plan_action(self, agent_data):
        """
        Get the plan and normal action list
        :param agent_data:
        """
        from wiseagent.action.base_action import BasePlanAction
        from wiseagent.core.agent_core import get_agent_core

        plan_action_list = []
        agent_core = get_agent_core()
        for action_item in agent_data.action_list:
            action_name = action_item.split(":")[0]
            action = agent_core.get_action(action_name)
            if isinstance(action, BasePlanAction):
                plan_action_list.append(action)
        return plan_action_list
