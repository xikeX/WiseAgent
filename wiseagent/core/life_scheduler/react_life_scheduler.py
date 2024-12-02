"""
Author: Huang Weitao
Date: 2024-10-27 20:55:53
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 17:07:42
Description: 
"""
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
    name: str = "ReActLifeSchedule"

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
                    agent_data.add_memory(UserMessage(content=rsp))
                # After executed the action, if the agent is dead, then break the loop
                logger.info(f"{command.action_method} executed. " + rsp)

            # Judge if the task is finished (To prevent the agent from being stuck in a loop)
            # check_end_prompt = (
            #     "Do task the user requirement? Analysize what you have done, If task is finished, return <END>, else return nothing"
            # )
            # rsp = self.llm_ask(check_end_prompt, agent_data.short_term_memory)
            # if any([tag in rsp for tag in ["<END>", "<End>", "<end>"]]):
            #     logger.info(f"Agent {agent_data.name} finsihed task")
            #     agent_data.sleep()


def get_life_scheduler():
    return ReActLifeSchedule()
