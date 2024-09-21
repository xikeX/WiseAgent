"""
Author: Huang Weitao
Date: 2024-09-21 02:48:15
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 12:41:54
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 02:36:10
Description: 
"""

import time
from typing import List

from pydantic import BaseModel

from wiseagent.action.plan_action import PlanAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.action_command import ActionCommand


@singleton
class ReActLifeSchedule(BaseModel):
    name: str = "ReActLifeSchedule"

    def life(self):
        agent_data = get_current_agent_data()
        self.human_life(agent_data)

    def react(self, agent_data: "AgentData"):
        agent_core = get_agent_core(agent_data)
        # select the plan action and normal action of the agent
        plan_action_list = []
        normal_action_list = []
        for action_name in agent_data.action_ability:
            action = agent_core.get_action(action_name)
            if isinstance(action, PlanAction):
                plan_action_list.append(action)
            else:
                normal_action_list.append(action)
        if len(plan_action_list) > 0:
            logger.info(
                f"Agent {agent_data.name} plan action more than one:{[plan_action.name for plan_action in plan_action_list]}"
            )
        while agent_data.is_alive:
            if agent_data.is_sleep:
                time.sleep(agent_data.heartbeat_interval)
                continue
            # Observe, because the message will automatically add to the short_term memory, so we don't need to add it manually
            command_list: List[ActionCommand] = []
            # Plan
            for plan_action in plan_action_list:
                rsp = plan_action.plan(agent_data, command_list)
                thought = rsp["thought"]
                command_list = rsp["command_list"]
                agent_data.add_memory(thought)
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
                # After executed the action, if the agent is dead, then break the loop


def get_life_scheduler():
    return ReActLifeSchedule()
