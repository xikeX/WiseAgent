"""
Author: Huang Weitao
Date: 2024-09-28 21:15:25
LastEditors: Huang Weitao
LastEditTime: 2024-10-03 11:39:17
Description: 
"""
import time
from typing import Any

from wxauto import WeChat

from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data

wechat = None


class WeChatActionData(BaseActionData):
    wechat_handle: Any = None


@singleton
class WeChatAction(BaseAction):
    """This is ActionCass to do wechat action, all the action will be play in Wechat Application"""

    action_description: str = " this class is to do wechat action."

    def init_agent(self, agent_data: Agent):
        agent_data.set_action_data(self.action_name, WeChatActionData())
        global wechat
        # will init the wechat in main thread
        if wechat is None:
            wechat = WeChat()

    def get_wechat_handle(self):
        agent_data = get_current_agent_data()
        wechat_action_data = agent_data.get_action_data(self.action_name)
        if wechat_action_data.wechat_handle is None:
            wechat_action_data.wechat_handle = wechat
        return wechat_action_data.wechat_handle

    @action()
    def get_chat_history(self, friend_name: str):
        """get the chat history with friend

        Args:
            friend_name (str): the friend name you want to get chat history. you must confirm the friend name is in your friend list.
        """
        wechat: WeChat = self.get_wechat_handle()
        # switch to chat page
        wechat.ChatWith(friend_name)
        chat_history = wechat.GetAllMessage()
        message_description = ""
        for msg in chat_history:
            if msg[0] == "Time":
                continue
            msg[0] == "Me" if msg[0] == "self" else msg[0]
            message_description += f"{msg[0]}: {msg[1]}\n"
        return message_description

    @action()
    def send_wechat_message(self, message: str, friend_name: str):
        """send message to friend

        Args:
            message (str): the message you want to send. you can use \n to split the message.
            friend_name (str): the friend name you want to send message. you must confirm the friend name is in your friend list.
        """

        wechat: WeChat = self.get_wechat_handle()
        wechat.SendMsg(message, friend_name)
        return f"{friend_name} has received the message and think is ok. DO NOT send the same message again."

    @action()
    def send_wechat_image(self, image_path: str, friend_name: str):
        """send image to friend.

        Args:
            image_path (str): the image path you want to send. you must confirm the image path is exist.
            friend_name (str): the friend name you want to send image. you must confirm the friend name is in your friend list.
        """

        wechat: WeChat = self.get_wechat_handle()
        wechat.SendFiles(image_path, friend_name)
        return f"{friend_name} has received the image and think is ok. DO NOT send the same image again."

    @action()
    def send_wechat_file(self, image_path: str, friend_name: str):
        """send file to friend.

        Args:
            image_path (str): the file path you want to send. you must confirm the file path is exist.
            friend_name (str): the friend name you want to send file. you must confirm the friend name is in your friend list.
        """

        wechat: WeChat = self.get_wechat_handle()
        wechat.SendFiles(image_path, friend_name)
        return f"{friend_name} has received the file and think is ok. DO NOT send the same file again."

    @action()
    def add_friend_to_listen_list(self, friend_name: str):
        """add friend to listen list

        Args:
            friend_name (str): the friend name you want to add to listen list. you must confirm the friend name is in your friend list.
        """

        wechat: WeChat = self.get_wechat_handle()
        wechat.AddListenChat(friend_name)
        return f"Add {friend_name} to listen list successfully. {friend_name} is in the listen list now. DO NOT add the same friend again."

    @action()
    def listen_for_new_wechat_message(self, friend_name: str = None, timeout=120):
        """listen for new wechat message

        Args:
            friend_name (str): the friend name you want to listen for new message. you must confirm the friend name is in your friend list. If you want to listen for all the new message, you can set the friend_name to None.
        """

        wechat: WeChat = self.get_wechat_handle()
        wechat.AddListenChat(friend_name)
        wait = 0
        while wait < timeout:
            msg = wechat.GetListenMessage()
            if len(msg) > 0:
                break
            time.sleep(1)
            wait += 1
        if len(msg) == 0:
            return "No new message"
        msg_desciption = ""
        for name in msg.keys():
            content = msg[name]
            msg_desciption += f"{name}: {content}\n"
        return "Received new message: " + msg_desciption


def get_action():
    return WeChatAction()
