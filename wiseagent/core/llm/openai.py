"""
Author: Huang Weitao
Date: 2024-09-22 12:30:13
LastEditors: Huang Weitao
LastEditTime: 2024-09-27 01:01:25
Description: 
"""
import os
import threading
from typing import Any, List

from openai import AsyncStream, OpenAI
from openai.types.chat import ChatCompletionChunk

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import STREAM_END_FLAG, Message
from wiseagent.common.singleton import singleton
from wiseagent.core.llm.base_llm import BaseLLM


@singleton
class OpenAIClient(BaseLLM):
    """"""

    llm_type: str = "OpenAI"
    base_url: str = ""
    openai_model_name: str = ""
    semaphore: Any = None
    temperature: float = 1
    # The number of thread that can call llm_ask at the same time
    semaphore_size: int = 5
    verbose: bool = False

    def __init__(
        self, api_key=None, base_url=None, model_name=None, semaphore_size=5, temperature=1, verbose=False
    ) -> None:
        super().__init__()
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.openai_model_name = model_name or os.environ.get("LLM_MODEL_NAME")
        self.semaphore_size = semaphore_size
        self.temperature = temperature
        self.semaphore = threading.Semaphore(self.semaphore_size)
        self.verbose = verbose or os.environ.get("LLM_VERBOSE") == "True"

    def create_client(self, api_key: str = None, base_url: str = None, temperature: float = 1):
        """Create a client for the OpenAI API use the given parameters."""
        return OpenAI(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
        )

    def llm_ask(
        self,
        memory: List[Message] = None,
        system_prompt: str = None,
        handle_stream_function=None,
        verbose: bool = None,
        base_url: str = None,
        model_name: str = None,
        api_key: str = None,
        temperature: float = 1,
    ) -> str:
        """Generate a response from the model using the given prompt.

        Args:
            memory (List[Message], optional): The conversation history. Defaults to None.
            system_prompt (str, optional): The system prompt. Defaults to None.
            handle_stream_function (function, optional): The function to handle the stream response. Defaults to None.
            verbose (bool, optional): Whether to print the response. Defaults to True.

            base_url (str, optional): The base url of the API. Defaults to None.
            model_name (str, optional): The name of the model. Defaults to None.
            api_key (str, optional): The API key. Defaults to None.

        Returns:
            str: The generated response.
        """
        # Each request will hold a semaphore to prevent the API from being called too frequently.
        verbose = verbose if verbose is not None else self.verbose
        with self.semaphore:
            client = self.create_client(api_key=api_key, base_url=base_url, temperature=temperature)
            memory = memory or []
            messages = self._build_messages(memory, system_prompt)
            response: AsyncStream[ChatCompletionChunk] = client.chat.completions.create(
                model=model_name or self.openai_model_name, messages=messages, stream=True, temperature=self.temperature
            )
            rsp = ""
            stream_message = ""

            for chunk in response:
                chunk_message = chunk.choices[0].delta.content or "" if chunk.choices else ""  # extract the message
                if verbose:
                    print(chunk_message, end="")
                for ch in chunk_message:
                    if handle_stream_function:
                        stream_message += ch
                        stream_message = handle_stream_function(stream_message)
                rsp += chunk_message
                # If the queue is not None: the response will be put into the queue.
            if handle_stream_function:
                handle_stream_function(STREAM_END_FLAG)
        return rsp


def get_llm(api_key=None):
    return OpenAIClient(api_key=api_key)
