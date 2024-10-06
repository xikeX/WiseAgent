"""
Author: Huang Weitao
Date: 2024-09-19 22:31:46
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:35:22
Description: 
"""

import importlib
import threading
from typing import Any, Dict

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG
from wiseagent.core.agent_core import AgentCore


@singleton
class LifeManager(BaseModel):
    """
    LifeManager is a singleton class responsible for managing the life cycle of agents.
    It ensures that each agent has only one life thread and provides a way to start and manage these threads.
    """

    # A map to store agent life threads, preventing multiple life threads for the same agent.
    agent_life_thread_map: dict = {}
    # A map to store different life schedulers, which are used to control the life cycle of agents.
    life_scheduler_map: Dict[str, Any] = {}

    def __init__(self):
        """Initialize the LifeManager and load all life schedulers from the configuration."""
        super().__init__()
        self._init_life_scheduler()

    def _init_life_scheduler(self):
        """Initialize and load life schedulers from the configured modules."""
        for life_scheduler_module_path in GLOBAL_CONFIG.life_scheduler_module_path:
            import_module = importlib.import_module(life_scheduler_module_path)
            if not hasattr(import_module, "get_life_scheduler") or not callable(
                getattr(import_module, "get_life_scheduler")
            ):
                raise Exception(
                    f"Life Scheduler Module {life_scheduler_module_path} does not have a get_life_scheduler method"
                )
            life_scheduler = import_module.get_life_scheduler()
            if life_scheduler.name not in self.life_scheduler_map:
                self.life_scheduler_map[life_scheduler.name] = life_scheduler

    def life(self, agent_data: AgentData):
        """Start a life of agent. Do not repeatly start the life of the agent.

        Args:
            agent_data (AgentData): The agent data.

        Raise:
            Exception: If the agent has already started life thread.
        """
        # Get the existing life thread for the agent, or create a new one.
        thread = self.agent_life_thread_map.get(agent_data.name, None) or threading.Thread(
            target=self._life, args=(agent_data,)
        )
        # Check if the thread is already running.
        if thread.is_alive():
            raise Exception(f"Agent {agent_data.name} has already started life thread")
        # Start the life thread for the agent.
        self.agent_life_thread_map[agent_data.name] = thread
        thread.start()

    def _life(self, agent_data: AgentData):
        """The actual life cycle of the agent, managed by the appropriate life scheduler.

        Args:
            agent_data (AgentData): The data of the agent.
        """
        # with agent_data will set the current_agent_data to the agent_data in the thread.
        with agent_data:
            life_scheduler = self.life_scheduler_map[agent_data.life_schedule_ability]
            life_scheduler.life()


def register(agent_core: AgentCore):
    if agent_core.life_manager is None:
        agent_core.life_manager = LifeManager()
