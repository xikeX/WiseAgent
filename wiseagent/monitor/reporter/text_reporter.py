'''
Author: Huang Weitao
Date: 2024-09-17 18:39:19
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 23:50:47
Description: ()
'''
import queue
from typing import List
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.protocol.message import STREAM_END_FLAG, ReportMessage
from wiseagent.monitor.reporter.base_reporter import BaseReporter
from wiseagent.config import logger
@singleton
class TextReporter(BaseReporter):
    name: str = "TextReporter"
    map_key_words: List[str] = ["Text"]
    def handle_stream_message(self, agentdata: AgentData, report_message:ReportMessage)-> bool:
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
    
    def handle_message(self, agentdata: AgentData, report_message:ReportMessage)-> bool:
        logger.info(f"{agentdata.name}: {report_message.content}")
        return True
def get_reporter() -> BaseReporter:
    return TextReporter()