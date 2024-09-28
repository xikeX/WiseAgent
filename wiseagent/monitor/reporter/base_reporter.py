"""
Author: Huang Weitao
Date: 2024-09-17 14:23:42
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 22:23:13
Description: 
"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData


class BaseReporter(BaseModel, ABC):
    """
    Base class for all reporters
    """

    name: str = "BaseReporter"

    @abstractmethod
    def handle_stream_message(self, agentdata: "AgentData", report_data):
        """
        Report data to the reporter
        """
        raise NotImplementedError

    @abstractmethod
    def handle_message(self, agentdata: "AgentData", report_data):
        """
        Report data to the reporter
        """
        raise NotImplementedError


def get_reporter(name: str):
    """
    subclass of BaseReporter must create this function
    """
