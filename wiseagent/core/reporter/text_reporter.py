"""
Author: Huang Weitao
Date: 2024-09-17 18:39:19
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 22:44:46
Description: ()
"""
import queue
from typing import List

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import STREAM_END_FLAG, Message
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent
from wiseagent.core.reporter.base_reporter import BaseReporter


@singleton
class TextReporter(BaseReporter):
    name: str = "TextReporter"

    def handle_stream_message(self, report_message: Message) -> bool:
        """the single agent report will report the message to the website."""
        logger.info(f"{report_message.send_from}:")
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

    def handle_message(self, report_message: Message) -> bool:
        logger.info(f"{report_message.send_from}: {report_message.content}")
        return True


def get_reporter() -> BaseReporter:
    return TextReporter()
