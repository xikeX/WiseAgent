"""
Author: Huang Weitao
Date: 2024-09-26 22:05:41
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 14:05:11
Description: The environment base class. 
The environment receives is the agent system moniter.
The enviroment repoter is the agent system receiver.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.base.base_component import EnvBaseReceiver, EnvBaseReporter
from wiseagent.monitor.monitor import Monitor
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.protocol.message import LLMHandleType, Message
from wiseagent.receiver.base_receiver import BaseReceiver


class BaseEnvironment(BaseModel):
    env_receiver: Any = None
    env_reporter: Any = None

    def __init__(self):
        super().__init__()
        self.env_receiver = EnvBaseReceiver(self.handle_message, self.handle_stream_message)
        self.env_reporter = EnvBaseReporter()
        pass

    def env_report(self, message: Message, disable_warning=False):
        if not disable_warning:
            if message.llm_handle_type == LLMHandleType.AI:
                logger.warning(
                    "The llm handle type is AI. This is not a good practice. "
                    "Because the llm will take the message from envionment as AI role."
                )
        self.env_reporter.add_message(message)

    @abstractmethod
    def handle_stream_message(self, agent_data: "AgentData", message: Message):
        """
        Handle stream message from agent system
        """

    @abstractmethod
    def handle_message(self, agent_data: "AgentData", message: Message):
        """
        Handle message from agent system
        """
