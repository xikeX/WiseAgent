"""
Author: Huang Weitao
Date: 2024-10-06 14:02:43
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:40:54
Description: 
"""
from abc import ABC
from typing import Any

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.protocol.message import Message


class EnvBaseReceiver(BaseReporter, ABC):
    """
    Base class for all reporters
    """

    name: str = "EnvReceiver"
    handle_message: Any = None
    handle_stream_message: Any = None

    def __init__(self, handle_message, handle_stream_message):
        super().__init__()
        if not handle_message:
            raise ValueError("handle_message is required")
        if not handle_stream_message:
            raise ValueError("handle_stream_message is required")
        self.handle_stream_message = handle_message
        self.handle_message = handle_stream_message
        # In here, will add the reporter to the reporter manager
        agent_core = get_agent_core()
        agent_core.get_monitor().resgiter(self)

    def handle_stream_message(self, agent_data: "AgentData", message: Message):
        """Fake function to avoid abstractmethod check in baseclass. This function will be replace in the __init__"""

    def handle_message(self, agent_data: "AgentData", message: Message):
        """Fake function to avoid abstractmethod check in baseclass. This function will be replace in the __init__"""


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
        self.repoter.add_message(message)
