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
from wiseagent.protocol.message import STREAM_END_FLAG, AIMessage, Message


@singleton
class DeepSeekAPI(BaseLLM):
    """DeepSeekAPI. Features: cheap, streaming support."""

    llm_name: str = "DeepSeek"
    base_url: str = "https://api.deepseek.com"
    semaphore: Any = None
    client: Any = None
    temperature: float = 1
    # The number of thread that can call llm_ask at the same time
    semaphore_size: int = 5

    def __init__(self, api_key=None) -> None:
        super().__init__()
        self.api_key = api_key
        self.semaphore = threading.Semaphore(self.semaphore_size)

    def check(self):
        return self.api_key is not None

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f"DeepSeekAPI: set api_key successfully")

    def llm_ask(
        self, memory: List[Message] = None, system_prompt: str = None, handle_stream_function=None, verbose: bool = True
    ) -> str:
        """Generate a response from the model using the given prompt.

        Args:
            memory (List[Message], optional): The conversation history. Defaults to None.
            system_prompt (str, optional): The system prompt. Defaults to None.
            queue (queue.Queue, optional): If provided, the response will be put into the queue for streaming. Defaults to None.

        Returns:
            str: The generated response.
        """
        # Each request will hold a semaphore to prevent the API from being called too frequently.
        with self.semaphore:
            memory = memory or []
            messages = self._build_messages(memory, system_prompt)
            response: AsyncStream[ChatCompletionChunk] = self.client.chat.completions.create(
                model="deepseek-chat", messages=messages, stream=True, temperature=self.temperature
            )
            collected_messages = []
            stream_message = ""
            for chunk in response:
                chunk_message = chunk.choices[0].delta.content or "" if chunk.choices else ""  # extract the message
                if verbose:
                    print(chunk_message, end="")
                stream_message += chunk_message
                if handle_stream_function:
                    stream_message = handle_stream_function(stream_message)
                collected_messages.append(chunk_message)
                # If the queue is not None: the response will be put into the queue.
            if handle_stream_function:
                handle_stream_function(STREAM_END_FLAG)
            rsp = "".join(collected_messages)
        return rsp


def get_llm(api_key=None):
    return DeepSeekAPI(api_key=api_key)
