"""
Author: Huang WeiTao
Date: 2024-10-29 21:17:42
LastEditors: Huang Weitao
LastEditTime: 2024-10-29 21:17:42
Description: This is a environment class that can change every editor into a chatbot.
"""


import queue
import re
import threading
import time
from datetime import datetime
from typing import Any

import pyautogui
import pyperclip
from pynput.keyboard import Controller, Key, KeyCode, Listener

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import (
    STREAM_END_FLAG,
    EnvironmentHandleType,
    FileUploadMessage,
    Message,
    UserMessage,
)
from wiseagent.common.singleton import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.base import BaseEnvironment

ENV_DESCRIPTION = """
The environment is a multi-agent environment, which includes {agent_name_list} and user (User).
"""
QUERY_HOTKEY = {Key.alt_l, KeyCode(char="q")}


@singleton
class EditorEnv(BaseEnvironment):
    """MultiAgentReporter is a class that can be used to report metrics to multiple agents."""

    run_thread: Any = None
    file_lock: Any = None
    environment_reporter: Any = None
    message_cache: Any = None
    agent_name_list: list[str] = None

    keyboard: Any = Controller()

    def __init__(self, agent_name_list: list[str] = None):
        super().__init__()
        """Initialize the MultiAgentReporter with a list of agents.
        
        Args:
            agent_name_list (list[str]): A list of agent names to report to. If none, all agents will be reported to.
        """
        self.file_lock = threading.Lock()
        # Initialize agent core and agent name list

        agent_core = get_agent_core()
        if not agent_name_list:
            # If agent_name_list is empty, use all available agents
            agent_name_list = [agent.name for agent in agent_core.agent_manager]
        agent_list = [agent for agent in agent_core.agent_manager if agent.name in agent_name_list] or []
        self.agent_name_list = [agent.name for agent in agent_list] or []
        if agent_name_list and (
            un_exists_agent_list := [
                agent_name for agent_name in agent_name_list if agent_name not in self.agent_name_list
            ]
        ):
            logger.error(f"Agent {un_exists_agent_list} is not exists.")

        for agent_data in agent_list:
            other_agent_name = [agent_name for agent_name in self.agent_name_list if agent_name != agent_data.name]
            env_description = ENV_DESCRIPTION.format(agent_name_list=",".join(other_agent_name))
            agent_data.current_environment = env_description

        self.message_cache = []

    def env_report(self, message: Message):
        """Report the message to the environment and log it to a file."""
        with self.file_lock:
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write(f"{message.send_from}->{message.send_to}:{message.content}\n\n")
        super().env_report(message)

    def add_agent(self, agent_name: str):
        """Add an agent to the environment."""
        if agent_name in self.agent_name_list:
            logger.error(f"Agent {agent_name} is already in the environment.")
            return

        agent_core = get_agent_core()
        if not agent_core.check_agent_exists(agent_name):
            logger.error(f"Agent {agent_name} is not exists.")
            return

        self.agent_name_list.append(agent_name)
        agent_list = [agent for agent in agent_core.agent_manager if agent.name in self.agent_name_list]
        for agent_data in agent_list:
            other_agent_name = [agent_name for agent_name in self.agent_name_list if agent_name != agent_data.name]
            env_description = ENV_DESCRIPTION.format(agent_name_list=",".join(other_agent_name))
            agent_data.current_environment = env_description

    def handle_message(self, message: Message) -> bool:
        """Get the message from the wiseagent system and send to th the wiseagent back."""
        # The Report Message and Receiver Message is to agent system. So in here will be a litle different
        if self.message_cache is not None:
            self.message_cache.append(message)

        if message.env_handle_type == EnvironmentHandleType.COMMUNICATION:
            if message.send_to == "user":
                self.output_use_editor(f"```markdown\nSend from {message.send_from} to user:\n{message.content}\n```\n")
            else:
                # this message is to other agent
                self.output_use_editor(
                    f"```markdown Send from {message.send_from} to {message.send_to}:\n{message.content}```"
                )
                self.env_report(message)
        elif message.env_handle_type == EnvironmentHandleType.CONTROL:
            pass
        elif message.env_handle_type == EnvironmentHandleType.THOUGHT:
            self.output_use_editor(f"```markdown\nThought of {message.send_from}:\n{message.content}\n```\n")
        elif message.env_handle_type == EnvironmentHandleType.COMMAND:
            pass
        elif message.env_handle_type == EnvironmentHandleType.BASE_ACTION_MESSAGE:
            pass
        elif message.env_handle_type == EnvironmentHandleType.FILE_UPLOAD:
            message: FileUploadMessage
            file_type_map = {
                "py": "python",
                "txt": "text",
                "md": "markdown",
                "json": "json",
                "yaml": "yaml",
                "yml": "yaml",
                "csv": "csv",
                "tsv": "tsv",
                "cpp": "cpp",
                "c": "c",
                "java": "java",
                "js": "javascript",
                "html": "html",
                "css": "css",
                "xml": "xml",
                "php": "php",
                "go": "go",
                "rb": "ruby",
                "rs": "rust",
                "swift": "swift",
                "kt": "kotlin",
                "dart": "dart",
                "ts": "typescript",
                "sql": "sql",
                "sh": "bash",
                "bat": "batch",
                "cmd": "batch",
                "ps1": "powershell",
            }
            if message.file_name.split(".")[-1] in file_type_map:
                file_type = file_type_map[message.file_name.split(".")[-1]]
            else:
                file_type = None
            if file_type is None:
                self.output_use_editor(f"```markdown\n The file:{message.file_name} is save\n```\n")
            else:
                self.output_use_editor(
                    f"\nfile_name:{message.file_name}\n```{file_type}\n{message.file_content.decode('utf-8')}\n```\n"
                )
        return True

    def handle_stream_message(self, message: Message) -> bool:
        """the single agent report will report the message to the website."""
        stream_queue = message.stream_queue
        while True:
            try:
                message_block = stream_queue.get(timeout=1)
            except queue.Empty:
                continue
            if message_block == None or message_block == STREAM_END_FLAG:
                break
            logger.info(message_block)
        return True

    def add_user_mesage(self, target_agent_name, content):
        """Add a user message to the environment and report it."""
        message = UserMessage(
            send_from="User",
            send_to=target_agent_name,
            env_handle_type=EnvironmentHandleType.COMMUNICATION,
            content=content,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.env_report(message)

    def listen_user_input(self):
        """Start a separate thread to listen for user input."""
        if self.run_thread is None:
            self.run_thread = threading.Thread(target=self._listen_user_input)
            self.run_thread.start()
        else:
            raise Exception("The env is already running")

    def _listen_user_input(self):
        """Handle user input in a loop, parsing the target agent name and message content."""
        current_keys = set()

        def on_press(key):
            # 将按下的键添加到当前按键集合中
            if key in [Key.alt_l, KeyCode(char="q"), KeyCode(char="w"), KeyCode(char="c")]:
                current_keys.add(key)

            # 检查当前按键集合是否包含所有需要的键
            if all(k in current_keys for k in QUERY_HOTKEY) and len(current_keys) == len(QUERY_HOTKEY):
                current_keys.clear()
                self.get_input_from_pyperclip()

        def on_release(key):
            # 从当前按键集合中移除释放的键
            try:
                current_keys.remove(key)
            except KeyError:
                pass

        # 开始监听键盘事件
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    def get_input_from_pyperclip(self):
        """Get input from the clipboard and process it."""
        time.sleep(1)
        pyautogui.hotkey("ctrl", "c")
        user_input = pyperclip.paste()
        print(f"get input from pyperclip{user_input}")
        if user_input:
            pattern = r"@(\w+?)\s"
            target_agent_name = re.findall(pattern, user_input)
            if len(target_agent_name) > 0:
                target_agent_name = target_agent_name[0]
                self.add_user_mesage(target_agent_name, user_input[len(target_agent_name) + 1 :])
            else:
                self.output_use_editor("Please input the correct format: @agent_name content")

    def output_use_editor(self, text):
        """Output the use editor message."""
        if text == "\n":
            pyautogui.hotkey("enter")
            return
        lines = [line for line in text.split("\n") if line.strip()] or [""]

        # 逐行处理并粘贴或模拟按下Enter键
        for i, line in enumerate(lines):
            pyperclip.copy(line)
            pyautogui.hotkey("ctrl", "v")
            if i < len(lines) - 1:  # 避免在最后一行后按Enter
                pyautogui.press("enter")
        # click down button twice
        pyautogui.hotkey("down")
        pyautogui.hotkey("down")
