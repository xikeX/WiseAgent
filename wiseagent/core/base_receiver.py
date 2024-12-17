"""
Author: Huang Weitao
Date: 2024-09-17 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:10:56
Description:  Base class for receivers, responsible for handling and processing messages.
"""
import queue
import threading
from typing import Any

from pydantic import BaseModel

from wiseagent.common.global_config import GlobalConfig
from wiseagent.common.logs import logger
from wiseagent.common.protocol_message import Message
from wiseagent.common.singleton import singleton
from wiseagent.core.agent_core import AgentCore, get_agent_core


@singleton
class BaseReceiver(BaseModel):
    """Base class for receivers."""

    # All the perceptron model. For difference agent, will use different perceptron model according to the Agent Data
    perceptron_list: list[Any] = []
    # A message queue to cache incoming messages.
    message_queue: Any = queue.Queue()
    # The thread that runs the receive loop.
    receive_thread: Any = None

    def __init__(self, global_config: GlobalConfig):
        super().__init__()
        self._init_perceptron(global_config)

    def _init_perceptron(self, global_config: GlobalConfig):
        # TODO: load perceptron model from config in the future
        pass

    def add_message(self, message: list[Message]):
        if not isinstance(message, list):
            message = [message]
        for m in message:
            if not isinstance(m, Message):
                logger.info(f"Message {m} is not a Message. andd will be ignored")
                continue
            # m.content = f"Message from <{m.send_from}> to <{m.send_to}>: {m.content}"
            self.message_queue.put(m)

    def _receive(self, agent_core: "AgentCore"):
        """Receive messages from the message queue and process them.

        Args:
            agent_core (AgentCore): The agent core object.
        """
        while agent_core.is_running:
            # Get the message from the queue, if the queue is empty, the get() method will block until a message is available
            message = None
            try:
                message = self.message_queue.get()
            except queue.Empty:
                continue

            # Determine the target agent(s) for the message.
            if message.send_to == "all":
                for agent in agent_core.agent_list:
                    if agent.name.lower() != message.send_from:
                        agent.add_memory(message, from_env=True)
            else:
                receive_agent = next(
                    (agent for agent in agent_core.agent_list if message.send_to == agent.name.lower()), None
                )
                if receive_agent:
                    receive_agent.add_memory(message, from_env=True)
                else:
                    self.message_queue.put(message)

    def run_receive_thread(self) -> bool:
        # Check if the thread is already running.
        if self.receive_thread is not None and self.receive_thread.is_alive():
            return True

        # Create or continue a thread to receive messages.
        try:
            self.receive_thread = self.receive_thread or threading.Thread(
                target=self._receive, args=(get_agent_core(),)
            )
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except Exception as e:
            print(e)
            return False

    def close(self):
        """Close the receive thread by joining it."""
        if self.receive_thread is not None and self.receive_thread.is_alive():
            self.receive_thread.join()
