'''
Author: Huang Weitao
Date: 2024-09-19 22:31:46
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 22:39:12
Description: 
'''

from typing import Dict
from pydantic import BaseModel

from wiseagent.life_manager.life_scheduler import BaseLifeScheduler
class LifeManager(BaseModel):
    # the map of agent_life_thread, to prevent agent start multiple life thread
    agent_life_thread_map: dict = {}
    life_scheduler_dict: Dict[str,BaseLifeScheduler] = {}