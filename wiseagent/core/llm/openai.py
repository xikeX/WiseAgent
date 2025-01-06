"""
Author: Huang Weitao
Date: 2024-09-22 12:30:13
LastEditors: Huang Weitao
LastEditTime: 2024-09-27 01:01:25
Description: 
"""
import os
import threading
from pathlib import Path
from typing import Any, List

from openai import AsyncStream, OpenAI
from openai.types.chat import ChatCompletionChunk

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import STREAM_END_FLAG, Message
from wiseagent.common.singleton import singleton
from wiseagent.core.llm.base_llm import BaseLLM

DEBUGE = False
llm_ask_times = 0


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
    count_tokens: bool = False
    tokenizer: Any = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def __init__(
        self,
        api_key=None,
        base_url=None,
        model_name=None,
        semaphore_size=5,
        temperature=None,
        verbose=True,
        count_tokens=None,
    ) -> None:
        super().__init__()
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL")
        self.openai_model_name = model_name or os.environ.get("LLM_MODEL_NAME")
        self.temperature = temperature or os.environ.get("LLM_TEMPERATURE", 0.5)
        self.count_tokens = count_tokens or (os.environ.get("LLM_COUNT_TOKENS", "False") == "True")
        self.semaphore_size = semaphore_size
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
        temperature: float = None,
        max_tokens: int = None,
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
            client = self.create_client(api_key=api_key, base_url=base_url, temperature=temperature or self.temperature)
            memory = memory or []
            messages = self._build_messages(memory, system_prompt)
            response: AsyncStream[ChatCompletionChunk] = client.chat.completions.create(
                model=model_name or self.openai_model_name,
                messages=messages,
                stream=True,
                temperature=self.temperature,
                max_tokens=max_tokens,
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
            # tiktoken
            if self.count_tokens:
                temp_model_name = model_name or self.openai_model_name
                if temp_model_name in ["deepseek-chat", "deepseek-coder"]:
                    self.count_tokens_fn(messages, rsp)
                pass
            if handle_stream_function:
                handle_stream_function(STREAM_END_FLAG)
            global DEBUGE, llm_ask_times
            if DEBUGE:
                os.makedirs("debug", exist_ok=True)
                with open("debug/llm.txt", "w", encoding="utf-8") as f:
                    for index, message in enumerate(messages[:-1]):
                        f.write(f"=============== {index+1} ==============\n")
                        f.write(f'role: {message["role"]}\n')
                        f.write(f'content: {message["content"]}\n')

                    f.write(f"=============== prompt ==============\n")
                    f.write(f'role: {messages[-1]["role"]}\n')
                    f.write(f'content: {messages[-1]["content"]}\n')
                    f.write(f"=============== response ==============\n")
                    f.write(f"content: {rsp}\n")

        return rsp

    def count_tokens_fn(self, message, rsp: str):
        """Count tokens for the given message and response."""
        from jinja2 import Template

        # Define the template
        template_str = """
        {% if not add_generation_prompt is defined %}{% set add_generation_prompt = false %}{% endif %}
        {{ bos_token }}{% for message in messages %}
        {% if message['role'] == 'user' %}{{ 'User: ' + message['content'] + '\n\n' }}
        {% elif message['role'] == 'assistant' %}{{ 'Assistant: ' + message['content'] + eos_token }}
        {% elif message['role'] == 'system' %}{{ message['content'] + '\n\n' }}
        {% endif %}{% endfor %}
        {% if add_generation_prompt %}{{ 'Assistant:' }}{% endif %}
        """

        # Define the template
        template = Template(template_str)
        # Define the data
        data = {"messages": message, "bos_token": "[BOS]", "eos_token": "[EOS]", "add_generation_prompt": True}

        # Render the template with the data
        rendered_text = template.render(data)
        # Cout the rendered text to the prompt
        if self.tokenizer is None:
            from transformers import AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(
                Path(__file__).parent / "deepseek-tokenizer", trust_remote_code=True
            )
        input_result = self.tokenizer.encode(rendered_text)
        output_result = self.tokenizer.encode(rsp)
        logger.info(f"input token number: {len(input_result)} output token number: {len(output_result)}")
        self.total_input_tokens += len(input_result)
        self.total_output_tokens += len(output_result)

    def reset_token_counter(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0


def get_llm(api_key=None):
    return OpenAIClient(api_key=api_key)
