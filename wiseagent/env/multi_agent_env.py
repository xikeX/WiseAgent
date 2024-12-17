import re
import threading
from datetime import datetime
from typing import Any

from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import (
    EnvironmentHandleType,
    Message,
    UserMessage,
)
from wiseagent.common.singleton import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.base import BaseEnvironment

ENV_DESCRIPTION = """
The environment is a multi-agent environment, which includes {agent_name_list} and user (User).
"""


@singleton
class MultiAgentEnv(BaseEnvironment):
    """MultiAgentReporter is a class that can be used to report metrics to multiple agents."""

    run_thread: Any = None
    environment_reporter: Any = None
    message_cache: Any = None
    stream_message_cache: Any = None
    agent_name_list: list[str] = None
    use_stream: bool = False
    thread_pool: Any = None

    def __init__(self, agent_name_list: list[str] = None, use_stream=False):
        super().__init__()
        """Initialize the MultiAgentReporter with a list of agents.
        
        Args:
            agent_name_list (list[str]): A list of agent names to report to. If none, all agents will be reported to.
        """
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

    def env_report(self, message: Message):
        """Report the message to the environment and log it to a file."""
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

    def handle_message(self, message: Message) -> bool:
        """Get the message from the wiseagent system and send to th the wiseagent back."""
        # The Report Message and Receiver Message is to agent system. So in here will be a litle different
        if self.message_cache is not None:
            self.message_cache.append(message)
        if message.env_handle_type == EnvironmentHandleType.COMMUNICATION:
            if message.send_to == "user":
                print(f"Receive Mesage:{message.content}")
            else:
                # this message is to other agent
                self.env_report(message)
        return True

    def handle_stream_message(self, message: Message) -> bool:
        """the single agent report will report the message to the website."""
        if self.message_cache is not None:
            self.message_cache.append(message)

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
        while True:
            user_input = input("User @name to chat agent")
            pattern = r"@(\w+?)\s"
            target_agent_name = re.findall(pattern, user_input)
            if len(target_agent_name) > 0:
                target_agent_name = target_agent_name[0]
                self.add_user_mesage(target_agent_name, user_input[len(target_agent_name) + 1 :])
            else:
                print("Please input the correct format")
