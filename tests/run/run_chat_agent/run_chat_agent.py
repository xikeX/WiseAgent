"""
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-26 23:25:01
Description: 
"""
import os
import time
from datetime import datetime

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.receiver.base_receiver import BaseReceiver

# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
chat_agent_config_file = os.path.join(current_folder, "chat_agent.yaml")


def test_main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_core._preparetion()
    receiver = agent_core.get_receiver()

    chat_agent_data = AgentData.from_yaml_file(chat_agent_config_file)

    agent_core.init_agent(chat_agent_data)

    agent_core.start_agent_life(chat_agent_data)
    while True:
        user_input = input("Chat:")
        receiver.add_user_message(user_input)


if __name__ == "__main__":
    test_main()
