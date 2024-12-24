"""
Author: Huang Weitao
Date: 2024-09-22 14:02:46
LastEditors: Huang Weitao
LastEditTime: 2024-09-22 15:47:46
Description: 
"""

import importlib
import os
import time

from loguru import logger
from pydantic import BaseModel

from wiseagent.common.global_config import GlobalConfig
from wiseagent.core.agent_core import AgentCore
from wiseagent.core.llm.base_llm import BaseLLM


class LLMManager(BaseModel):
    llm_map: dict = {}

    def __init__(self, global_config: GlobalConfig):
        super().__init__()
        start = time.time()
        self.init_llm_map(global_config)
        end = time.time()
        logger.info(f"LLMManager init time: {end - start} s")

    def init_llm_map(self, global_config: GlobalConfig):
        for llm_module_path in global_config.llm_module_path:
            llm_module = importlib.import_module(llm_module_path)
            if not hasattr(llm_module, "get_llm") or not callable(getattr(llm_module, "get_llm")):
                raise Exception(f"Module {llm_module_path} does not have a callable get_llm function")
            llm_model = llm_module.get_llm()
            self.llm_map[llm_model.llm_type] = llm_model

    def register(self, obj: BaseLLM):
        self.llm_map[obj.llm_type] = obj

    def get_llm(self, llm_type=None):
        if llm_type is None or llm_type not in self.llm_map:
            llm_type = os.environ.get("LLM_TYPE", None)

            # update function
            if llm_type and llm_type.lower() == "openai":
                llm_type = "OpenAI"
            else:
                llm_type = llm_type

            if llm_type is None or llm_type not in self.llm_map:
                raise Exception(f"Default LLM {llm_type} not found")
            logger.info(f"Using default LLM {llm_type}")
        return self.llm_map[llm_type]
