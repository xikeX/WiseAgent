"""
Author: Huang Weitao
Date: 2024-09-21 22:09:35
LastEditors: Huang Weitao
LastEditTime: 2024-10-03 22:22:56
Description: 
"""

from datetime import datetime

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction
from wiseagent.agent_data.base_agent_data import get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import EnvironmentHandleType, Message


@singleton
class Chat(BaseAction):
    action_type: str = "NormalAction"
    action_description: str = "Chat with another agent or human."

    def __init__(self):
        super().__init__()

    @action()
    def chat(self, send_to: str, message: str, wait_for_response=False):
        """
        Chat with another agent or human. If there is no task to do, you can use wait_for_response to wait for a response or a new task.

        Args:
            send_to (str): The name of the agent or human to chat with.
            message (str): The message to send.
            wait_for_response (bool, optional): Whether to wait for a response.

        Example:
            >>> chat("Alice", "Hello, how are you?")
            If you want to wait for a response, you can set wait_for_response to True.
            >>> chat("Bob", "I'm fine, thank you. How about you?", wait_for_response=True)
        """
        agent_core = get_agent_core()
        agent_data = get_current_agent_data()
        # Send message to the agent
        target_agent = send_to
        report_message = Message(
            send_from=agent_data.name,
            send_to=target_agent.strip(),
            env_handle_type=EnvironmentHandleType.COMUNICATION,
            content=message.strip(),
            time_stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            track=[f"file:{__file__}\nfuntion:chat"],
        )
        agent_core.monitor.add_message(report_message)
        output = f"Send message to {target_agent} successfully. {target_agent} have check, if you have no longer to take action, try to wait. Do not send the same message again."
        if wait_for_response:
            agent_data.observe(with_reset=True)
            agent_data.sleep()
        return output


def get_action():
    return Chat()
