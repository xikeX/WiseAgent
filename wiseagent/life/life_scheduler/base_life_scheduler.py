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

from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import Message, UserMessage


class BaseLifeScheduler(BaseModel, ABC):
    """Base class for all life schedules"""

    name: str = ""

    @abstractmethod
    def life(self):
        pass

    def llm_ask(self, prompt, memory: List[Message] = None, system_prompt: str = None):
        """Ask the LLM to generate a response to the given prompt."""
        agent_data: AgentData = get_current_agent_data()
        agent_core = get_agent_core()
        if memory is None:
            # Get the lastest memory from the agent autumaticly
            memory = agent_data.get_last_memory()
        memory = memory + [UserMessage(content=prompt)]
        llm = agent_core.get_llm(agent_data.llm_ability["llm_name"])
        if not llm:
            raise Exception("LLM not found")
        if not llm.check() and agent_data.llm_ability["api_key"]:
            llm.set_api_key(agent_data.llm_ability["api_key"])
        rsp = llm.llm_ask(memory=memory, system_prompt=system_prompt)
        return rsp
