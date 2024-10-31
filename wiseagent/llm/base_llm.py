"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:34:55
Description: 
"""

import queue
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from wiseagent.protocol.message import Message


class BaseLLM(BaseModel, ABC):
    api_key: str = ""
    base_url: str = ""
    llm_name: str = ""

    @abstractmethod
    def llm_ask(self, memory: List[Message] = None, system_prompt: str = None, handle_stream_function=None) -> str:
        """Ask the LLM a question and return the answer"""
        pass

    def set_key(self, api_key: str):
        self.api_key = api_key

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    def check(self):
        return False

    def _build_messages(
        self, memories: List[Message], system_prompt: str = None, user_prompt: str = None
    ) -> List[dict]:
        """Build the messages for the API request."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for memory in memories:
            # If the message if from AI, the message.role is set to "assistant", otherwise it is set to "user".
            # If the message.role is not set, it is set to "user".
            messages.append({"role": memory.llm_handle_type.value, "content": memory.content})

        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})
        return messages
