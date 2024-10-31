import os
import queue
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from altair import Stream
from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.base.base import BaseEnvironment
from wiseagent.protocol.message import (
    STREAM_END_FLAG,
    EnvironmentHandleType,
    FileUploadMessage,
    Message,
    UserMessage,
)

ENV_DESCRIPTION = """
The environment is a multi-agent environment, which includes {agent_name_list} and user (User).
"""


@singleton
class MultiAgentEnv(BaseEnvironment):
    """MultiAgentReporter is a class that can be used to report metrics to multiple agents."""

    run_thread: Any = None
    file_lock: Any = None
    environment_reporter: Any = None
    message_cache: Any = None
    agent_name_list: list[str] = None
    use_stream: bool = False
    thread_pool: Any = None

    def __init__(self, agent_name_list: list[str] = None, use_stream=False):
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
            agent_name_list = [agent.name for agent in agent_core.agent_list]
        agent_list = [agent for agent in agent_core.agent_list if agent.name in agent_name_list] or []
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

        if use_stream:
            self.use_stream = True
            self.thread_pool = ThreadPoolExecutor(max_workers=5)

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
        agent_list = [agent for agent in agent_core.agent_list if agent.name in self.agent_name_list]
        for agent_data in agent_list:
            other_agent_name = [agent_name for agent_name in self.agent_name_list if agent_name != agent_data.name]
            env_description = ENV_DESCRIPTION.format(agent_name_list=",".join(other_agent_name))
            agent_data.current_environment = env_description

    def handle_file_upload_stream_message(self, file_upload_stream_message: FileUploadMessage) -> bool:
        # get the sub message from upload stream message
        current_message = ""
        while True:
            try:
                current_message = file_upload_stream_message.stream_queue.get(timeout=30)
            except Exception as e:
                logger.error(f"Error while getting message from file upload stream message: {e}")
                return False
            # write the message to the code file
            if current_message == STREAM_END_FLAG:
                break
            else:
                try:
                    # Create the parent folder of the file if it does not exist
                    parent_folder = os.path.dirname(file_upload_stream_message.appendix["file_name"])
                    if not os.path.exists(parent_folder):
                        os.makedirs(parent_folder)
                    with open(file_upload_stream_message.appendix["file_name"], "a") as f:
                        f.write(current_message)
                except Exception as e:
                    logger.error(f"Error while writing message to file: {e}")

    def handle_message(self, message: Message) -> bool:
        """Get the message from the wiseagent system and send to th the wiseagent back."""
        # The Report Message and Receiver Message is to agent system. So in here will be a litle different
        if self.message_cache is not None:
            self.message_cache.append(message)
        if message.env_handle_type == EnvironmentHandleType.COMUNICATION:
            if message.send_to == "user":
                print(f"Receive Mesage:{message.content}")
                with self.file_lock:
                    with open("test.txt", "a", encoding="utf-8") as f:
                        f.write(f"{message.send_from}->{message.send_to}:{message.content}\n\n")
            else:
                # this message is to other agent
                self.env_report(message)
        return True

    def handle_stream_message(self, message: Message) -> bool:
        """the single agent report will report the message to the website."""
        if message.env_handle_type == EnvironmentHandleType.FILE_UPLOAD:
            # Create a new thread from the thread pool to handel file_upload_stream_message
            self.thread_pool.submit(self.handle_file_upload_stream_message, message)

        return True

    def add_user_mesage(self, target_agent_name, content):
        """Add a user message to the environment and report it."""
        message = UserMessage(
            send_from="User",
            send_to=target_agent_name,
            env_handle_type=EnvironmentHandleType.COMUNICATION,
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
        while True:
            user_input = input("User @name to chat agent")
            pattern = r"@(\w+?)\s"
            target_agent_name = re.findall(pattern, user_input)
            if len(target_agent_name) > 0:
                target_agent_name = target_agent_name[0]
                self.add_user_mesage(target_agent_name, user_input[len(target_agent_name) + 1 :])
            else:
                print("Please input the correct format")
