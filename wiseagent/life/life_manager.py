"""
Author: Huang Weitao
Date: 2024-09-19 22:31:46
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 12:42:53
Description: 
"""

import importlib
import threading
from typing import Dict

from pydantic import BaseModel

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.config import GLOBAL_CONFIG
from wiseagent.core.agent_core import AgentCore
from wiseagent.life.life_scheduler import BaseLifeScheduler


@singleton
class LifeManager(BaseModel):
    # the map of agent_life_thread, to prevent agent start multiple life thread
    agent_life_thread_map: dict = {}
    life_schedule_map: Dict[str, BaseLifeScheduler] = {}

    def __init__(self, **data):
        self._init_life_scheduler()

    def _init_life_scheduler(self):
        for life_scheduler_module_path in GLOBAL_CONFIG.life_scheduler_module_path:
            import_module = importlib.import_module(life_scheduler_module_path)
            if not hasattr(import_module, "get_life_scheduler") and not callable(
                getattr(import_module, "get_life_scheduler")
            ):
                raise Exception(
                    f"Life Scheduler Module {life_scheduler_module_path} does not have a get_life_scheduler method"
                )
            life_schedule = import_module.get_life_schedule()
            if life_schedule not in self.life_schedule:
                self.life_schedule_map[life_schedule.name] = life_schedule

    def life(self, agent_data: AgentData):
        """Start a life of agent. Do not repeatly start the life of the agent.

        Args:
            agent_data (AgentData): The agent data.

        Raise:
            Exception: If the agent has already started life thread.
        """
        # Get the life thread of the agent
        thread = self.agent_life_thread_map.get(agent_data.agent_name, None) or threading.Thread(
            target=self._life, args=(agent_data,)
        )
        # If the agent has already started life thread, raise an exception
        if thread.is_alive():
            raise Exception(f"Agent {agent_data.agent_name} has already started life thread")
        # Start the life thread of the agent
        self.agent_life_thread_map[agent_data.agent_name] = thread
        thread.start()

    def _life(self, agent_data: AgentData):
        with agent_data:
            life_scheduler = self.life_schedule_map[agent_data.life_scheduler_name]
            life_scheduler.life()


def register(agent_core: AgentCore):
    if agent_core.life_manager is None:
        agent_core.life_manager = LifeManager()
