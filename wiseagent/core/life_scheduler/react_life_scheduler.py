"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 17:07:42
Description: 
"""
import json
import time
from random import randint
from typing import List

from wiseagent.action.base_action import BasePlanAction
from wiseagent.common.logs import logger
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.protocol_message import AIMessage, CommandMessage, UserMessage
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler


@singleton
class ReActLifeSchedule(BaseLifeScheduler):
    def life(self):
        """Main life cycle method for the agent."""
        agent_data = get_current_agent_data()
        self.react(agent_data)

    def react(self, agent_data: "Agent"):
        """React to the environment and execute actions based on the agent's state."""
        agent_core = get_agent_core()

        # Separate plan actions and normal actions
        plan_action_list = []
        normal_action_list = []
        for action_item in agent_data.action_list:
            action_name = action_item.split(":")[0]
            action = agent_core.get_action(action_name)
            if isinstance(action, BasePlanAction):
                plan_action_list.append(action)
            else:
                normal_action_list.append(action)

        # Log if there are multiple plan actions
        if len(plan_action_list) > 1:
            logger.info(
                f"Agent {agent_data.name} plan action more than one:{[plan_action.action_name for plan_action in plan_action_list]}"
            )

        # Main loop
        while agent_data.is_alive:
            if not agent_data.is_activate:
                agent_data.wake_up_event.wait()
                agent_data.wake_up_event.clear()
                continue
            # Make Plan
            command_list: List[ActionCommand] = []
            for plan_action in plan_action_list:
                thought, command_list = plan_action.plan(command_list)
                plan_memory = ""
                if thought:
                    plan_memory += thought
                if command_list:
                    thought += json.dumps([i.to_dict() for i in command_list], ensure_ascii=False)
                if plan_memory:
                    agent_data.add_memory(AIMessage(content=thought))

            # Act/ReAct
            command: ActionCommand
            for command in command_list:
                current_action = agent_core.get_action(command.action_name)
                rsp = ""
                try:
                    if hasattr(current_action, command.action_method) and callable(
                        getattr(current_action, command.action_method)
                    ):
                        # current_action.action_method(self,agent_data,command.params)
                        method = getattr(current_action, command.action_method)
                        rsp = method(**command.args)
                    else:
                        rsp = f"{command.action_method} not found"
                except Exception as e:
                    rsp = f"Exception: {str(e)}"
                if rsp:
                    agent_data.add_memory(UserMessage(content=rsp))
                # After executed the action, if the agent is dead, then break the loop
                logger.info(f"{command.action_method} executed. " + rsp if rsp else "")


def get_life_scheduler():
    return ReActLifeSchedule()
