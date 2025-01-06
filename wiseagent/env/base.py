"""
Author: Huang Weitao
Date: 2024-09-26 22:05:41
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 14:05:11
Description: The environment base class. 
The environment receives is the agent system moniter.
The environment repoter is the agent system receiver.
"""

from abc import ABC
from typing import Any

from pydantic import BaseModel

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import LLMHandleType, Message
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.reporter.base_reporter import BaseReporter


class EnvBaseReceiver(BaseReporter, ABC):
    """
    Base class for all reporters
    """

    name: str = "EnvReceiver"
    _handle_message: Any = None
    _handle_stream_message: Any = None

    def __init__(self, handle_message, handle_stream_message):
        super().__init__()
        if not handle_message:
            raise ValueError("handle_message is required")
        if not handle_stream_message:
            raise ValueError("handle_stream_message is required")
        self._handle_message = handle_message
        self._handle_stream_message = handle_stream_message
        # In here, will add the reporter to the reporter manager
        agent_core = get_agent_core()
        agent_core.get_monitor().register(self)

    def close(self):
        agent_core = get_agent_core()
        agent_core.get_monitor().unregister(self)

    def handle_stream_message(self, message: Message) -> bool:
        """Fake function to avoid abstractmethod check in baseclass. This function will be replace in the __init__"""
        self._handle_stream_message(message)
        return True

    def handle_message(self, message: Message) -> bool:
        """Fake function to avoid abstractmethod check in baseclass. This function will be replace in the __init__"""
        self._handle_message(message)
        return True


class EnvBaseReporter(BaseModel):
    """
    Base class for environment reporter
    """

    repoter: Any = None

    def __init__(self):
        super().__init__()
        agent_core = get_agent_core()
        self.repoter = agent_core.get_receiver()

    def add_message(self, message: Message):
        if self.repoter:
            self.repoter.add_message(message)


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

    def handle_stream_message(self, message: Message) -> bool:
        """
        Handle stream message from agent system.
        If use stream message in Wiseagent and send it to the environment, the message will be handled by this function.
        """
        raise NotImplementedError

    def handle_message(self, message: Message) -> bool:
        """
        Handle message from agent system.
        If normal action message in Wiseagent and send it to the environment, the message will be handled by this function.
        """
        raise NotImplementedError

    def close(self):
        self.env_receiver.close()
