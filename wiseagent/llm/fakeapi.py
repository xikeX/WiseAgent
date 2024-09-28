import queue
import uuid
from mailbox import Message
from typing import Any, Callable, List, Union

from wiseagent.llm.base_llm import BaseLLM


class FakeApi(BaseLLM):
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key
        self.model = "fakeapi"

    def llm_ask(self, memory: List[Message] = None, system_prompt: str = None, queue: queue.Queue = None) -> str:
        """Ask the LLM a question and return the answer"""
        message = self._build_message(memory, system_prompt)
        return f" fake answer :{str(uuid.uuid4())[-12:]}"
