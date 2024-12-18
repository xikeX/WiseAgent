"""
Author: Huang Weitao
Date: 2024-09-19 22:31:46
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:35:22
Description: 
"""

import importlib
import threading
import time
from typing import Any, Dict

from pydantic import BaseModel

from wiseagent.common.global_config import GlobalConfig
from wiseagent.common.logs import logger
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent
from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler


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

    def __init__(self, global_config: GlobalConfig):
        """Initialize the LifeManager and load all life schedulers from the configuration."""
        super().__init__()
        start = time.time()
        self._init_life_scheduler(global_config)
        end = time.time()
        logger.info(f"LifeManager init time: {end - start}")

    def _init_life_scheduler(self, global_config):
        """Initialize and load life schedulers from the configured modules."""
        for life_scheduler_module_path in global_config.life_scheduler_module_path:
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

    def register(self, life_scheduler: BaseLifeScheduler):
        """Add a life scheduler to the life manager."""
        self.life_scheduler_map[life_scheduler.name] = life_scheduler

    def life(self, agent_data: Agent, new_thread):
        """Start a life of agent. Do not repeatly start the life of the agent.

        Args:
            agent_data (AgentData): The agent data.

        Raise:
            Exception: If the agent has already started life thread.
        """
        # Get the existing life thread for the agent, or create a new one.
        agent_data._is_alive = True
        if new_thread:
            thread = self.agent_life_thread_map.get(agent_data.name, None) or threading.Thread(
                target=self._life, args=(agent_data,)
            )
            # Check if the thread is already running.
            if thread.is_alive():
                raise Exception(f"Agent {agent_data.name} has already started life thread")
            # Start the life thread for the agent.
            self.agent_life_thread_map[agent_data.name] = thread
            thread.start()
        else:
            self._life(agent_data)

    def _life(self, agent_data: Agent):
        """The actual life cycle of the agent, managed by the appropriate life scheduler.

        Args:
            agent_data (AgentData): The data of the agent.
        """
        # with agent_data will set the current_agent_data to the agent_data in the thread.
        with agent_data:
            life_scheduler = self.life_scheduler_map[agent_data.life_schedule_config]
            life_scheduler.life()
