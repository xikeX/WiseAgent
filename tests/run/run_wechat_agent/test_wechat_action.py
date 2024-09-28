"""
Author: Huang Weitao
Date: 2024-09-18 22:31:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 20:28:59
Description: 
"""
import os
import threading
import time
from datetime import datetime

from wiseagent.action.normal_action.wechat import WeChatAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.monitor.monitor import Monitor
from wiseagent.protocol.message import Message, MessageType
from wiseagent.receiver.base_receiver import BaseReceiver

# get the current folder of the file
current_folder = os.path.dirname(os.path.abspath(__file__))
chat_agent_config_file = os.path.join(current_folder, "wechat_agent.yaml")


def test_main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_core.preparetion()
    receiver = BaseReceiver()

    chat_agent_data = AgentData.from_yaml_file(chat_agent_config_file)

    agent_core.init_agent(chat_agent_data)

    wechat_action = WeChatAction()

    def main():
        with chat_agent_data:
            # friend_list = wechat_action.get_wachat_friend_list()
            # print(friend_list)
            chat_history = wechat_action.get_chat_history("程序员小c")
            print(chat_history)
            result = wechat_action.send_wechat_message("你好", "程序员小c")
            print(result)
            result = wechat_action.send_wechat_image(r"C:\Users\90545\Desktop\186789536_0_final.png", "程序员小c")
            print(result)
            result = wechat_action.send_wechat_file(r"C:\Users\90545\Desktop\凸优化作业.md", "程序员小c")
            print(result)
            result = wechat_action.add_friend_to_listen_list("文件传输助手")
            print(result)
            result = wechat_action.listen_for_new_wechat_message("文件传输助手")
            print(result)

    run = threading.Thread(target=main).start()

    while True:
        time.sleep(1)
    # agent_core.start_agent_life(chat_agent_data)
    # while True:
    #     user_input = input("Chat:")
    #     receiver_message = Message(
    #         send_from="User",
    #         send_to="Bob",
    #         message_type=MessageType.COMUNICATION,
    #         content=user_input,
    #         timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #     )
    #     receiver.add_message(receiver_message)


if __name__ == "__main__":
    test_main()
