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
import time
from typing import Any, List

from pydantic import BaseModel

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import Message
from wiseagent.common.singleton import singleton
from wiseagent.config.global_config import GlobalConfig
from wiseagent.core.agent_core import AgentCore, get_agent_core
from wiseagent.core.reporter.base_reporter import BaseReporter


@singleton
class BaseMonitor(BaseModel):
    reporter_list: List[BaseReporter] = []
    # The stream_queue_list is used to store the stream data
    reporter_cache: Any = queue.Queue()
    report_thread: Any = None

    def __init__(self, global_config: GlobalConfig):
        super().__init__()
        # init the reporter model use global config
        start = time.time()
        self.init_reporter(global_config)
        end = time.time()
        logger.info(f"Init Monitor time: {end - start} s")

    def init_reporter(self, global_config: GlobalConfig):
        """Init the reporter model use global config"""
        for reporter_module_path in global_config.reporter_module_path:
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
            message = self.reporter_cache.get()
            self.handle_report(message)

    def handle_report(self, message: Message):
        """Report the message to reporter(Which is the receiver of the environment)
        One message can only be reported to one reporter.
        # TODO: hope in the future, one message can be reported to multiple reporter. But this must consider the stream message
        Args:
            message (Message): The message to be reported.
        """
        is_solved = False
        for reporter in self.reporter_list:
            if message.is_stream:
                is_solved = reporter.handle_stream_message(message)
            else:
                is_solved = reporter.handle_message(message)
            if is_solved:
                break

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
