"""
Author: Huang Weitao
Date: 2024-09-17 18:39:19
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 22:44:46
Description: ()
"""
import queue
from typing import List

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.protocol.message import STREAM_END_FLAG, Message


@singleton
class TextReporter(BaseReporter):
    name: str = "TextReporter"

    def handle_stream_message(self, agentdata: AgentData, report_message: Message) -> bool:
        """the single agent report will report the message to the website."""
        logger.info(f"{agentdata.name}:")
        stream_queue = report_message.stream_queue
        while True:
            try:
                message_block = stream_queue.get(timeout=1)
            except queue.Empty:
                continue
            if message_block == None or message_block == STREAM_END_FLAG:
                break
            logger.info(message_block)
        return True

    def handle_message(self, agentdata: AgentData, report_message: Message) -> bool:
        logger.info(f"{agentdata.name}: {report_message.content}")
        return True


def get_reporter() -> BaseReporter:
    return TextReporter()
