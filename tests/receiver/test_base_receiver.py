'''
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 23:45:14
Description: 
'''
import os
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.message import Message, ReceiveMessage
from wiseagent.core.agent_core import get_agent_core
from wiseagent.receiver.base_receiver import BaseReceiver
# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
all_receiver_config_file = os.path.join(current_folder, "all_receiver.yaml")
network_receiver_config_file = os.path.join(current_folder, "network_receiver.yaml")
text_receiver_config_file = os.path.join(current_folder, "text_receiver.yaml")

def test_main():
    agent_core = get_agent_core()
    agent_core._init_receiver()
    assert agent_core.receiver is not None, ""
    agent_core.start_pre_function()
    receiver = BaseReceiver()
    assert receiver == agent_core.receiver, ""
    # Add AgentData to agent_core
    all_receiver_agent_data = AgentData.from_yaml_file(all_receiver_config_file)
    network_receiver_agent_data = AgentData.from_yaml_file(network_receiver_config_file)
    text_receiver_agent_data = AgentData.from_yaml_file(text_receiver_config_file)
    agent_core.init_agent_data(all_receiver_agent_data)
    agent_core.init_agent_data(network_receiver_agent_data)
    agent_core.init_agent_data(text_receiver_agent_data)
    text_message = ReceiveMessage(
        send_from = "User", send_to = "Text_receiver", receive_type = "text",
        content = "Hello, Text_receiver!",type = "text", timestamp = "2023-10-01 12:00:00")
    receiver.add_message(text_message)
    
    network_message = ReceiveMessage(
        send_from = "User", send_to = "Network_receiver", receive_type = "network",
        content = "Hello, network_message!",type = "network", timestamp = "2023-10-01 12:00:00")
    receiver.add_message(network_message)
    
    network_message.send_to = "All_receiver"
    text_message.send_to = "All_receiver"
    receiver.add_message([network_message,text_message])
    
    normal_message = Message(
        send_from = "User", send_to = "Network_receiver", receive_type = "network",
        content = "Hello, network_message!",type = "network", timestamp = "2023-10-01 12:00:00")
    receiver.add_message(normal_message)
if __name__ == "__main__":
    test_main()