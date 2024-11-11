"""
Author: Huang Weitao
Date: 2024-09-21 02:48:15
LastEditors: Huang Weitao
LastEditTime: 2024-09-22 11:33:25
Description: 
"""
from typing import List

from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler


@singleton
class AutoStartLifeScheduler(BaseLifeScheduler):
    name: str = "AutoStartLifeScheduler"

    def life(self):
        agent_data = get_current_agent_data()
        self.human_life(agent_data)

    def auto_start_mode(self, agent_data: "Agent"):
        agent_core = get_agent_core()
        action_list = []
        for action_item in agent_data.action_list:
            action_name = action_item.split(":")[0]
            action = agent_core.get_action(action_name)
            action_list.append(action)
        while agent_data.is_alive:
            if not agent_data.is_activate():
                # Wait for wakeup()
                agent_core.wake_up_event.wait()
            command_list: List[ActionCommand] = []
            # Check Start
            rsp = ""
            for action in action_list:
                rsp += action.check_start(command_list=command_list)
            agent_data.add_memory(rsp)
            # Act
            for command in command_list:
                action = agent_core.get_action(command.action_name)
                rsp = ""
                if hasattr(action, command.action_method) and callable(getattr(action, command.action_method)):
                    action_method = getattr(action, command.action_method)
                    rsp = action_method(**command.args)
                else:
                    rsp = f"{command.action_method} not found"
                if rsp:
                    agent_data.add_memory(command.action_name, rsp)


def get_life_scheduler():
    return AutoStartLifeScheduler()
