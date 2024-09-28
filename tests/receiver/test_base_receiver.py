"""
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-26 22:00:54
Description: 
"""
import os
import time

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import Message, MessageType
from wiseagent.receiver.base_receiver import BaseReceiver

# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
all_receiver_config_file = os.path.join(current_folder, "all_receiver.yaml")
network_receiver_config_file = os.path.join(current_folder, "network_receiver.yaml")
text_receiver_config_file = os.path.join(current_folder, "text_receiver.yaml")


def test_main():
    agent_core = get_agent_core()
    agent_core._init_monitor()
    assert agent_core.receiver is not None, ""
    receiver = BaseReceiver()
    assert receiver == agent_core.receiver, ""
    # Add AgentData to agent_core
    all_receiver_agent_data = AgentData.from_yaml_file(all_receiver_config_file)
    network_receiver_agent_data = AgentData.from_yaml_file(network_receiver_config_file)
    text_receiver_agent_data = AgentData.from_yaml_file(text_receiver_config_file)
    agent_core.init_agent(all_receiver_agent_data)
    agent_core.init_agent(network_receiver_agent_data)
    agent_core.init_agent(text_receiver_agent_data)
    agent_core.start_pre_function()
    text_message = Message(
        send_from="User",
        send_to="Text_receiver",
        message_type=MessageType.COMUNICATION,
        content="Hello, Text_receiver!",
        type="text",
        timestamp="2023-10-01 12:00:00",
    )
    receiver.add_message(text_message)

    network_message = Message(
        send_from="User",
        send_to="Network_receiver",
        message_type=MessageType.COMUNICATION,
        content="Hello, network_message!",
        type="network",
        timestamp="2023-10-01 12:00:00",
    )
    receiver.add_message(network_message)

    network_message.send_to = "All_receiver"
    text_message.send_to = "All_receiver"
    receiver.add_message([network_message, text_message])

    normal_message = Message(
        send_from="User",
        send_to="Network_receiver",
        message_type=MessageType.COMUNICATION,
        content="Hello, network_message!",
        type="network",
        timestamp="2023-10-01 12:00:00",
    )
    receiver.add_message(normal_message)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    test_main()
