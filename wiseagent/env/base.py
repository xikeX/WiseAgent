"""
Author: Huang Weitao
Date: 2024-09-26 22:05:41
LastEditors: Huang Weitao
LastEditTime: 2024-09-26 22:30:51
Description: The environment base class. 
The environment receives is the agent system moniter.
The enviroment repoter is the agent system receiver.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.monitor.monitor import Monitor
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.receiver.base_receiver import BaseReceiver


class EnvBaseReceiver(BaseReporter, ABC):
    """
    Base class for all reporters
    """

    name: str = "EnvReceiver"
    handle_message_callback: Any = None
    handle_stream_message_callback: Any = None

    def __init__(self, handle_message_callback, handle_stream_message_callback):
        super().__init__()
        self.handle_message_callback = handle_message_callback
        self.handle_stream_message_callback = handle_stream_message_callback
        # In here, will add the reporter to the reporter manager
        base_monitor = Monitor()
        base_monitor.resgiter(self)

    def handle_stream_message(self, agentdata: "AgentData", report_data):
        """
        Report data to the reporter
        """
        self.handle_stream_message_callback(agentdata, report_data)

    def handle_message(self, agentdata: "AgentData", report_data):
        """
        Report data to the reporter
        """
        self.handle_message_callback(agentdata, report_data)


def get_reporter():
    # the only function that can use in this function is add_message
    return BaseReceiver()
