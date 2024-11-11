"""
Author: Huang Weitao
Date: 2024-09-21 02:23:21
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 02:32:50
Description: 
"""
from typing import List

from wiseagent.action.base_action import BasePlanAction
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler


@singleton
class HumanLifeScheduler(BaseLifeScheduler):
    name: str = "HumanLifeScheduler"

    def life(self):
        agent_data = get_current_agent_data()
        self.human_life(agent_data)

    def human_life(self, agent_data: "Agent"):
        plan_action_list = []
        normal_action_list = []
        agent_core = get_agent_core()
        for action_item in agent_data.action_list:
            action_name = action_item.split(":")[0]
            action = agent_core.get_action(action_name)
            if isinstance(action, BasePlanAction):
                plan_action_list.append(action)
            else:
                normal_action_list.append(action)
        while agent_data.is_alive:
            if not agent_data.is_activate:
                agent_data.wake_up_event.wait()
                continue
            # Plan
            command_list: List[ActionCommand] = []
            for plan_action in plan_action_list:
                rsp = plan_action.plan(agent_data, command_list)
                thought = rsp["thought"]
                command_list = rsp["command_list"]
                agent_data.add_memory(thought)
            # Self Start
            for normal_action in normal_action_list:
                if not any([normal_action.name == command.action_name for command in command_list]):
                    rsp = normal_action.check_start()
                    agent_data.add_memory(rsp)
            # Act/ReAct
            command: ActionCommand
            for command in command_list:
                current_action = agent_core.get_action(command.action_name)
                rsp = ""
                if hasattr(current_action, command.action_method) and callable(
                    getattr(current_action, command.action_method)
                ):
                    # current_action.action_method(self,agent_data,command.params)
                    method = current_action.get_method(action.action_method)
                    rsp = method(**command.args)
                else:
                    rsp = f"{command.action_method} not found"
                if rsp:
                    agent_data.add_memory(rsp)


def get_life_scheduler():
    return HumanLifeScheduler()
