"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-10-05 11:13:57
Description: 
"""
import time
from random import randint
from typing import List

from wiseagent.action.plan_action.base_plan_action import BasePlanAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.life.life_scheduler.base_life_scheduler import BaseLifeScheduler
from wiseagent.protocol.action_command import ActionCommand
from wiseagent.protocol.message import AIMessage, CommandMessage, UserMessage


@singleton
class ReActLifeSchedule(BaseLifeScheduler):
    name: str = "ReActLifeSchedule"

    def life(self):
        """Main life cycle method for the agent."""
        agent_data = get_current_agent_data()
        self.react(agent_data)

    def react(self, agent_data: "AgentData"):
        """React to the environment and execute actions based on the agent's state."""
        agent_core = get_agent_core()

        # Separate plan actions and normal actions
        plan_action_list = []
        normal_action_list = []
        for action_config in agent_data.action_ability:
            action_name = action_config["action_name"]
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
            if agent_data.is_sleep:
                time.sleep(agent_data.heartbeat_interval)
                if agent_data.observe(with_reset=True):
                    agent_data.wake_up()
                continue
            # Make Plan
            command_list: List[ActionCommand] = []
            for plan_action in plan_action_list:
                if rsp := plan_action.plan(command_list):
                    thought = rsp["thoughts"]
                    agent_data.add_memory(AIMessage(content=thought))
                    if "action_command_list" in rsp and rsp["action_command_list"]:
                        command_list.extend(rsp["action_command_list"])
                    # Report the thought and command
                    # agent_core.monitor.add_message(
                    #     CommandMessage(content="```json\n" + json.dumps([c.model_dump() for c in rsp["action_command_list"]],ensure_ascii=False) + "\n```")
                    # )

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
                    agent_data.add_memory(AIMessage(content=rsp))
                # After executed the action, if the agent is dead, then break the loop
                logger.info(f"{command.action_method} executed. " + rsp)

            # Judge if the task is finished (To prevent the agent from being stuck in a loop)
            prompt = "Do task finished? Analysize what you have done, Output <END> to stop and <CONTINUE> to continue."
            rsp = self.llm_ask(prompt, agent_data.short_term_memory)
            if any([tag in rsp for tag in ["<END>", "<End>", "<end>"]]):
                logger.info(f"Agent {agent_data.name} finsihed task")
                agent_data.sleep()

            # Sleep, forbidding the agent act too fast, and lead to cost too much money
            logger.info(f"Agent {agent_data.name} is sleeping 5 seconds")
            time.sleep(randint(5, 10))


def get_life_scheduler():
    return ReActLifeSchedule()
