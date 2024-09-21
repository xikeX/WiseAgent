"""
Author: Huang Weitao
Date: 2024-09-21 22:09:35
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 23:00:32
Description: 
"""

import time
from datetime import datetime

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseAction
from wiseagent.agent_data.base_agent_data import get_current_agent_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import Message, ReportMessage


class Chat(BaseAction):
    action_name: str = "Chat"
    action_type: str = "NormalAction"
    action_description: str = "Chat with another agent or human."

    @action()
    def chat(self, name: str, message: str, wait_for_response: bool = False):
        """
        Chat with another agent or human.

        Args:
            name (str): The name of the agent or human to chat with.
            message (str): The message to send.
            wait_for_response (bool, optional): Whether to wait for a response. Defaults to False.

        Example:
            >>> chat("Alice", "Hello, how are you?")
            If you want to wait for a response, you can set wait_for_response to True.
            >>> chat("Bob", "I'm fine, thank you. How about you?", wait_for_response=True)
        """
        agent_core = get_agent_core()
        agent_data = get_current_agent_data()
        # Send message to the agent
        report_message = ReportMessage(
            send_from=agent_data.name,
            send_to=name.strip(),
            content=message.strip(),
            time_stamp=datetime.now().format("%Y-%m-%d %H:%M:%S"),
            track=[f"file:{__file__}\nfuntion:chat"],
        )
        agent_core.monitor.add_message(report_message)
        output = f"Send message to {name} successfully."

        if wait_for_response:
            while True:
                new_message = agent_data.check_new_message()
                respond_message = [messgae for messgae in new_message if messgae.send_from == name]
                if len(respond_message) > 0:
                    # TODO: May be need to remove the repond memory in the agent data
                    respond_str = "\n".join([message.content for message in respond_message])
                    output += f" {name} respond: {respond_str}"
                    break
                time.sleep(0.5)
        return output
