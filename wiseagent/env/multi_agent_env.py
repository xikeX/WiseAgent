import queue
import re
import threading
import time
from datetime import datetime
from typing import Any
from venv import logger

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.base import EnvBaseReceiver, get_reporter
from wiseagent.protocol.message import STREAM_END_FLAG, Message, MessageType

ENV_DESCRIPTION = """
你现在一个聊天室环境，这里有
{agent_name_list}和用户（User）
现在你们要解决一个问题：
请问是3.9大还是3.11大？
"""


@singleton
class MultiAgentEnv(BaseModel):
    """MultiAgentReporter is a class that can be used to report metrics to multiple agents."""

    run_thread: Any = None
    file_lock: Any = None
    environment_reporter: Any = None
    receivers: Any = None
    message_cache: Any = None
    agent_history: dict = {}

    def __init__(self):
        super().__init__()
        """Initialize the MultiAgentReporter with a list of agents."""
        self.environment_reporter = get_reporter()
        self.receivers = EnvBaseReceiver(
            handle_message_callback=self.handle_message, handle_stream_message_callback=self.handle_stream_message
        )
        self.file_lock = threading.Lock()
        # After init the environment, will send a environment description message to the agent.
        agent_core = get_agent_core()
        agent_list = agent_core.agent_list
        agent_names = [agent.name for agent in agent_list]
        self.file_lock = threading.Lock()
        for cur_agent in agent_names:
            other_agent_name = [agent_name for agent_name in agent_names if agent_name != cur_agent]
            env_description = ENV_DESCRIPTION.format(agent_name_list=",".join(other_agent_name))
            messgae = Message(
                send_from="User",
                send_to=cur_agent,
                message_type=MessageType.COMUNICATION,
                content=env_description,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                track=[f"file:{__file__}\nfunction:__init__"],
            )
            self.env_report(messgae)
            time.sleep(5)

    def env_report(self, message):
        with self.file_lock:
            with open("test.txt", "a", encoding="utf-8") as f:
                f.write(f"{message.send_from}->{message.send_to}:{message.content}\n\n")
        if self.message_cache:
            self.message_cache.put(message)
            self.message
        self.environment_reporter.add_message(message)

    def handle_message(self, agent_data: AgentData, message):
        """Get the message from the wiseagent system and send to th the wiseagent back."""
        # The Report Message and Receiver Message is to agent system. So in here will be a litle different
        if message.message_type == MessageType.COMUNICATION:
            if message.send_to == "user":
                print(f"Receive Mesage:{message.content}")
                with self.file_lock:
                    with open("test.txt", "a", encoding="utf-8") as f:
                        f.write(f"{message.send_from}->{message.send_to}:{message.content}\n\n")
            else:
                # this message is to other agent
                self.env_report(message)

        elif message.message_type == MessageType.THOUGHT:
            # This is a thought of the agent
            # TODO: add the thought to the agent
            with open("thought.txt", "a", encoding="utf-8") as f:
                f.write(f"{message.send_from}->{message.send_to}:{message.content}\n\n")
            pass

    def handle_stream_message(self, agent_data: AgentData, message: Message):
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

    def run_env(self):
        if run_thread is None:
            run_thread = threading.Thread(target=self._run_env)
            run_thread.start()
        else:
            raise Exception("The env is already running")

    def _run_env(self):
        while True:
            user_input = input("User @name to chat agent")
            pattern = r"@(\w+?)\s"
            target_agent_name = re.findall(pattern, user_input)
            if len(target_agent_name) > 0:
                target_agent_name = target_agent_name[0]
                message = Message(
                    send_from="User",
                    send_to=target_agent_name,
                    message_type=MessageType.COMUNICATION,
                    content=user_input.replace("@", ""),
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                self.env_report(message)
            else:
                print("Please input the correct format")
