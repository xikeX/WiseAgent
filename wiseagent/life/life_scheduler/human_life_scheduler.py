"""
Author: Huang Weitao
Date: 2024-09-21 02:23:21
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 02:32:50
Description: 
"""
import time
from typing import List

from wiseagent.action.plan_action.base_plan_action import PlanAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.life.life_scheduler.base_life_scheduler import BaseLifeScheduler
from wiseagent.protocol.action_command import ActionCommand


@singleton
class HumanLifeScheduler(BaseLifeScheduler):
    name: str = "HumanLifeScheduler"

    def life(self):
        agent_data = get_current_agent_data()
        self.human_life(agent_data)

    def human_life(self, agent_data: "AgentData"):
        plan_action_list = []
        normal_action_list = []
        agent_core = get_agent_core()
        for action_name in agent_data.action_ability:
            action = agent_core.get_action(action_name)
            if isinstance(action, PlanAction):
                plan_action_list.append(action)
            else:
                normal_action_list.append(action)
        while agent_data.is_alive:
            if agent_data.is_sleep:
                time.sleep(agent_data.heartbeat_interval)
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
                if hasattr(current_action, command.action_method) and callable(
                    getattr(current_action, command.action_method)
                ):
                    # current_action.action_method(self,agent_data,command.params)
                    method = current_action.get_method(action.action_method)
                    rsp = method(agent_data, **command.parameters)
                agent_core.add_memory(rsp)


def get_life_scheduler():
    return HumanLifeScheduler()
