"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 21:06:34
Description: 
"""

import time
from random import randint
from typing import List

from pydantic import BaseModel

from wiseagent.action.plan_action.base_plan_action import BasePlanAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.life.life_scheduler.base_life_scheduler import BaseLifeScheduler
from wiseagent.llm.llm_manager import ask
from wiseagent.protocol.action_command import ActionCommand
from wiseagent.protocol.message import Message, ThoughtMessage


@singleton
class ReActLifeSchedule(BaseLifeScheduler):
    name: str = "ReActLifeSchedule"

    def life(self):
        agent_data = get_current_agent_data()
        self.react(agent_data)

    def react(self, agent_data: "AgentData"):
        agent_core = get_agent_core()
        # select the plan action and normal action of the agent
        plan_action_list = []
        normal_action_list = []
        for action_config in agent_data.action_ability:
            action_name = action_config["action_name"]
            action = agent_core.get_action(action_name)
            if isinstance(action, BasePlanAction):
                plan_action_list.append(action)
            else:
                normal_action_list.append(action)
        if len(plan_action_list) > 1:
            logger.info(
                f"Agent {agent_data.name} plan action more than one:{[plan_action.action_name for plan_action in plan_action_list]}"
            )
        while agent_data.is_alive:
            if agent_data.is_sleep:
                time.sleep(agent_data.heartbeat_interval)
                if agent_data.observe(with_reset=True):
                    agent_data.wake_up()
                continue
            # Observe, because the message will automatically add to the short_term memory, so we don't need to add it manually
            command_list: List[ActionCommand] = []
            # Plan
            for plan_action in plan_action_list:
                if rsp := plan_action.plan(command_list):
                    thought = rsp["thoughts"]
                    agent_data.add_memory(thought)
                    if "action_command_list" in rsp and rsp["action_command_list"]:
                        command_list.extend(rsp["action_command_list"])
            # Act/ReAct
            command: ActionCommand
            for command in command_list:
                current_action = agent_core.get_action(command.action_name)
                rsp = ""
                if hasattr(current_action, command.action_method) and callable(
                    getattr(current_action, command.action_method)
                ):
                    # current_action.action_method(self,agent_data,command.params)
                    method = getattr(current_action, command.action_method)
                    rsp = method(**command.args)
                else:
                    rsp = f"{command.action_method} not found"
                if rsp:
                    agent_data.add_memory(rsp)
                # After executed the action, if the agent is dead, then break the loop
                logger.info(rsp)
            # 判断是否需要结束
            prompt = "Do you finsish your task? output:Yes/No"
            rsp = self.llm_ask(prompt, agent_data.short_term_memory)
            if any([tag in rsp for tag in ["Yes", "yes"]]):
                agent_data.sleep()
            logger.info(f"Agent {agent_data.name} is sleeping 5 seconds")
            time.sleep(randint(5, 10))


def get_life_scheduler():
    return ReActLifeSchedule()
