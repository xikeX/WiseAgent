"""
Author: Huang Weitao
Date: 2024-09-21 02:48:15
LastEditors: Huang Weitao
LastEditTime: 2024-09-27 00:01:12
Description: 
"""
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.protocol.message import Message
from wiseagent.receiver.perceptron import BasePerceptron


@singleton
class TextPerceptron(BasePerceptron):
    "The messsage of text. Usually in single agent system. And User is the sender"
    name: str = "TextPerceptron"
    cause_by: str = "Text"

    def handle_message(self, agent_data: AgentData, msg: Message):
        # Add the received message to the short-term memory
        agent_data.add_memory(msg, from_env=True)
        logger.info(f"Received message: {msg}")


def get_perceptron():
    return TextPerceptron()
