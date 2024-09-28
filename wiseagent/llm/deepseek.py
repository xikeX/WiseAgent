"""
Author: Huang Weitao
Date: 2024-09-22 12:30:13
LastEditors: Huang Weitao
LastEditTime: 2024-09-27 01:01:25
Description: 
"""
import queue
import threading
from typing import Any, Callable, List, Union

from openai import AsyncStream, OpenAI
from openai.types.chat import ChatCompletionChunk

from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.llm.base_llm import BaseLLM
from wiseagent.protocol.message import AIMessage, Message


@singleton
class DeepSeekAPI(BaseLLM):
    """DeepSeekAPI. Features: cheap, streaming support."""

    llm_name: str = "DeepSeek"
    base_url: str = "https://api.deepseek.com"
    semaphore: Any = None
    client: Any = None
    temperature: float = 1

    def __init__(self, api_key=None) -> None:
        super().__init__()
        self.api_key = api_key
        if self.api_key is None:
            logger.warning(f"DeepSeekAPI: api_key is None")
        else:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.semaphore = threading.Semaphore(5)  # The API can be called at most 5 times per second.

    def check(self):
        return self.api_key is not None

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f"DeepSeekAPI: set api_key successfully")

    def llm_ask(self, memory: List[Message] = None, system_prompt: str = None, queue: queue.Queue = None) -> str:
        """Gernerate a response from the model using the given prompt.

        Args:
            memory (List[Memory], optional): The memory to use for the response. Defaults to None.
            system_prompt (str, optional): The system prompt to use for the response. Defaults to None.
            queue (queue.Queue, optional): If need a stream process, the queue is used to store the response. Defaults to None.
        """
        # Each request will hold a semaphore to prevent the API from being called too frequently.
        with self.semaphore:
            memory = memory or []
            messages = self._build_messages(memory, system_prompt)
            response: AsyncStream[ChatCompletionChunk] = self.client.chat.completions.create(
                model="deepseek-chat", messages=messages, stream=True, temperature=self.temperature
            )
            collected_messages = []
            for chunk in response:
                chunk_message = chunk.choices[0].delta.content or "" if chunk.choices else ""  # extract the message
                print(chunk_message, end="")
                collected_messages.append(chunk_message)
                # If the queue is not None: the response will be put into the queue.
                if queue:
                    queue.put(chunk_message)
            rsp = "".join(collected_messages)
        return rsp


def get_llm(api_key=None):
    return DeepSeekAPI(api_key=api_key)
