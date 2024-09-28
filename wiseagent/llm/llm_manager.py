"""
Author: Huang Weitao
Date: 2024-09-22 14:02:46
LastEditors: Huang Weitao
LastEditTime: 2024-09-22 15:47:46
Description: 
"""

import importlib

from pydantic import BaseModel

from wiseagent.config.global_config import GLOBAL_CONFIG
from wiseagent.core.agent_core import AgentCore


class LLMManager(BaseModel):
    llm_map: dict = {}

    def __init__(self):
        super().__init__()
        for llm_module_path in GLOBAL_CONFIG.llm_module_path:
            llm_module = importlib.import_module(llm_module_path)
            if not hasattr(llm_module, "get_llm") or not callable(getattr(llm_module, "get_llm")):
                raise Exception(f"Module {llm_module_path} does not have a callable get_llm function")
            llm_model = llm_module.get_llm()
            self.llm_map[llm_model.llm_name] = llm_model

    def get_llm(self, llm_name):
        if llm_name not in self.llm_map:
            raise Exception(f"LLM {llm_name} not found")
        return self.llm_map[llm_name]


def register(agent_core: "AgentCore"):
    agent_core.llm_manager = LLMManager()
