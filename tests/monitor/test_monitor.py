"""
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:10:17
Description: 
"""
import os
import queue
import time
from datetime import datetime

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.monitor.monitor import Monitor
from wiseagent.protocol.message import STREAM_END_FLAG, Message
from wiseagent.receiver.base_receiver import BaseReceiver

# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
test_report_config_file = os.path.join(current_folder, "test_report.yaml")


def test_main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_core._preparetion()
    receiver = agent_core.get_receiver()

    chat_agent_data = AgentData.from_yaml_file(test_report_config_file)

    agent_core.init_agent(chat_agent_data)

    agent_core.start_agent_life(chat_agent_data)
    while True:
        user_input = input("Chat:")
        receiver_message = Message(
            send_from="User",
            send_to="Bob",
            content=user_input,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        receiver.add_message(receiver_message)


if __name__ == "__main__":
    test_main()
