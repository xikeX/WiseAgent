'''
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 23:50:38
Description: 
'''
import os
import time
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.protocol.message import STREAM_END_FLAG, Message, ReportMessage
from wiseagent.core.agent_core import get_agent_core
from wiseagent.monitor.monitor import Monitor
import queue
# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
test_report_config_file = os.path.join(current_folder, "test_report.yaml")

def test_main():
    agent_core = get_agent_core()
    agent_core._init_monitor()
    assert agent_core.monitor is not None, ""
    monitor = Monitor()
    assert monitor == agent_core.monitor, ""
    # Add AgentData to agent_core
    test_report_agent_data = AgentData.from_yaml_file(test_report_config_file)
    agent_core.init_agent_data(test_report_agent_data)
    agent_core.start_pre_function()
    text_message = ReportMessage(
        send_from = "Test_report", send_to = "User", report_type = "Text",
        content = "Hello, Test_report!",type = "text", timestamp = "2023-10-01 12:00:00")
    monitor.add_message(text_message)
    stream_queue = queue.Queue()
    network_message = ReportMessage(
        send_from = "Test_report", send_to = "User", report_type = "Text",is_stream = True,stream_queue = stream_queue,
        type = "network", timestamp = "2023-10-01 12:00:00")
    monitor.add_message(network_message)
    for i in range(10):
        stream_queue.put(f"{i} message block send")
        time.sleep(0.5)
    stream_queue.put(STREAM_END_FLAG)
    normal_message = Message(
        send_from = "Test_report", send_to = "User", report_type = "Text",
        content = "Hello, network_message!",type = "network", timestamp = "2023-10-01 12:00:00")
    monitor.add_message(normal_message)
if __name__ == "__main__":
    test_main()