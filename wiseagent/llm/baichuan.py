"""
Author: Huang We

from wiseagent.llm.base_llm import BaseLLMitao
Date: 2024-09-22 12:30:13
LastEditors: Huang Weitao
LastEditTime: 2024-09-22 15:52:27
Description: 
"""
import queue
from typing import Any, Callable, List, Union

import dashscope

from wiseagent.common.annotation import singleton
from wiseagent.llm.base_llm import BaseLLM
from wiseagent.protocol.message import Message


@singleton
class Baichuan2Api(BaseLLM):
    """
    百川智能2的API接口实现类。
    该类是使用了积灵平台的API，而不是直接调用百川智能2的API。
    使用积灵平台的API，可以实现更灵活的调用方式，并可以方便地切换API提供方。

    当时因为百川智能的API还没有公开，所以使用了积灵平台的API。
    """

    llm_name: str = "Baichuan2"

    def __init__(self, api_key=None) -> None:
        super().__init__()
        dashscope.api_key = api_key

    def check(self):
        return dashscope.api_key is not None

    def set_api_key(self, api_key):
        dashscope.api_key = api_key
        # TODO: Reflesh the client

    def llm_ask(self, memory: List[Message] = None, system_prompt: str = None, queue: queue.Queue = None) -> str:
        # TODO: Implement the method to ask the LLM
        pass


def get_llm():
    return Baichuan2Api()
