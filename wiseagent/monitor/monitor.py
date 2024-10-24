"""
Author: Huang Weitao
Date: 2024-09-17 14:23:28
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 22:39:58
Description: The Monitor class is used to monitor the agent and report the status to the reporter.
I hope this class can support streaming data and normal data.

This will be single thread to monitor the agent and report the status to the reporter.
# TODO: switch to multi-thread
# NOTE: In current version, the monitor will not report more than one message in one time.
"""

import importlib
import queue
import threading
from typing import Any, List

from pydantic import BaseModel
from typing_extensions import Unpack

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG, logger
from wiseagent.core.agent_core import AgentCore, get_agent_core
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.protocol.message import Message


@singleton
class Monitor(BaseModel):
    reporter_list: List[BaseReporter] = []
    # The stream_queue_list is used to store the stream data
    reporter_cache: Any = queue.Queue()
    report_thread: Any = None

    def __init__(self):
        super().__init__()
        # init the reporter model use global config
        for reporter_module_path in GLOBAL_CONFIG.reporter_module_path:
            # register the perecptron module
            import_module = importlib.import_module(reporter_module_path)
            if not hasattr(import_module, "get_reporter") or not callable(getattr(import_module, "get_reporter")):
                raise Exception(f"Reporter Module {reporter_module_path} does not have a get_reporter method")
            reporter = import_module.get_reporter()
            if reporter not in self.reporter_list:
                self.reporter_list.append(reporter)

    def resgiter(self, reporter: BaseReporter):
        """Register a reporter to the monitor.
        NOTE : The EnvReceiver is a Reporter of the agent system.
        Args:
            reporter (BaseReporter): The reporter to register."""
        if reporter not in self.reporter_list:
            self.reporter_list.append(reporter)

    def add_message(self, msg: Message):
        if not isinstance(msg, Message):
            logger.warning(f"Message {msg} is not a Message, and will be ignored")
            return
        self.reporter_cache.put(msg)

    def _report(self, agent_core: "AgentCore"):
        """Receive messages from the message queue and process them.
        Args:
            agent_core (AgentCore): The agent core object.
        """
        while agent_core.is_running:
            # get the message from the queue, if the queue is empty, the get() method will block until a message is available
            message = None
            try:
                message = self.reporter_cache.get(timeout=1)
            except queue.Empty:
                continue
            agent = None
            for agent in agent_core.agent_list:
                if agent.name == message.send_from:
                    break
            if agent is None:
                logger.error(f"Agent {message.send_from} not found")
                continue
            self.handle_report(agent, message)

    def handle_report(self, agentdata: AgentData, message: Message):
        """This function will send the message to the each of the reporter in the reporter_list."""
        for reporter in self.reporter_list:
            if message.is_stream:
                reporter.handle_stream_message(agentdata, message)
            else:
                reporter.handle_message(agentdata, message)

    def run_report_thread(self) -> bool:
        # check if the thread is running
        if self.report_thread is not None and self.report_thread.is_alive():
            return True
        # create or continue a thread to receive message
        try:
            self.report_thread = self.report_thread or threading.Thread(target=self._report, args=(get_agent_core(),))
            self.report_thread.daemon = True
            self.report_thread.start()
            return True
        except Exception as e:
            print(e)
            return False

    def close(self):
        if self.report_thread is not None:
            self.report_thread.join()


def register(agent_core: "AgentCore"):
    """Register the receiver to the agent core."""
    agent_core.monitor = Monitor()
    agent_core._prepare_function_list.append(agent_core.monitor.run_report_thread)
    agent_core._close_function_list.append(agent_core.monitor.close)
