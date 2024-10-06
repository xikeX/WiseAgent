"""
Author: Huang Weitao
Date: 2024-09-21 19:19:27
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 20:16:33
Description: 
"""
import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseActionData
from wiseagent.action.plan_action.base_plan_action import BasePlanAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.common.parse_llm_respond import parse_json_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.action_command import ActionCommand, parse_command
from wiseagent.protocol.message import ThoughtMessage

INSTRUCTION_PROMPT = """
## Plan List
{plan_list}

{current_task}
## Instruction
Please generate a plan for the agent to complete the task.
Your respond must contain the thought and a json for action command list.
The json format is:
```json
[
    {{
        "action_name": "action_name",
        "action_method" : "action_method",
        "args": {{
            "arg1": "arg1",
            "arg2": "arg2"
            ...
        }}
    }}
    ...
]
``
"""
EXPERIENCE = """
Example 1:
Requirment: The user asks me to respond to the question: "What is 2Co + 2Fe = ?"
Thought: I need to calculate the result of the equation 2Co + 2Fe = ? This is a simple arithmetic problem. I will reply to the user with the result.
```json
[
    {
        "action_name": "Chat",
        "action_method" : "chat",
        "args": {
            "send_to": "user",
            "message": "The result of the equation 2Co + 2Fe = ? is 4Co + 2Fe. But I thik Coffee is better. Ah...",
            "wait_for_response": true
        }
    }
]

Example 2:
Requirment: The user asks me to respond to the question: "Who is the author of the book ?'
Thought: I do not kown the user is asking for which book. I need to ask the user for more information. I will reply to the user with the question.
```json
[
    {
        "action_name": "Chat",
        "action_method" : "chat",
        "args": {
            "send_to": "user",
            "message": "Which book are you asking for?"
            "wait_for_response": true
        }
    }
]

Example 3:
Requirment: I do not have received any request from the user.
Thought: There is no requirement, so i will use the wait for task action to wait for the user's request.
```json
[
    {
        "action_name":"MethodPlanAction",
        "action_method":"wait_for_task"
    }
]
```
Example 4:
Requirment: Open the wechat and send message to the "溪客", message is "今晚10点开会"
```json
[
    {
        "action_name": "WeChatAction",
        "action_method" : "send_wechat_message",
        "args": {
            "friend_name": "溪客",
            "message": "今晚10点开会"
        }
    }
]
```

Example 5:
Requirment: Search the arxiv article contain LLM and Agent.
```json
[
   {
        "action_name": "ArxivAction",
        "action_method": "search_arxiv_article",
        "args": {
            "search_terms": "\\\"LLM\\\" AND \\\"Agent\\\"",
            "pass_days": 1
        }
    } 
]
"""


class MethodPlanActionData(BaseActionData):
    """The data of the method plan action"""

    instruction_prompt: str = INSTRUCTION_PROMPT
    expericence: str = EXPERIENCE
    plan_list: List[dict] = []
    current_plan_index: int = 0


@singleton
class MethodPlanAction(BasePlanAction):
    """The planner of the agent, which is used to plan the action of the agent"""

    action_name: str = "MethodPlan"
    max_tries: int = 3

    def plan(self, command_list: List[ActionCommand]) -> Dict:
        """Execute the plan action
        Args:
            command_list (List[ActionCommand]): The command list of the agent

        Returns:
            Dict: The result of the plan action, which may include thoughts, action command list, etc.
        """
        agent_data: AgentData = get_current_agent_data()
        plan_action_data = agent_data.get_action_data("MethodPlanAction")
        system_prompt = agent_data.get_agent_system_prompt(agent_example=plan_action_data.expericence)
        instruction_prompt = plan_action_data.instruction_prompt.format(
            plan_list=self.get_plan_list_description(plan_action_data.plan_list),
            current_task=("## Current Task\n", plan_action_data.plan_list[plan_action_data.current_plan_index])
            if len(plan_action_data.plan_list) > plan_action_data.current_plan_index
            else "",
        )
        rsp = self.llm_ask(instruction_prompt, system_prompt=system_prompt)
        json_data, error = parse_json_data(rsp)
        i = 0
        while error and i < self.max_tries:
            prompt = instruction_prompt + f"Your respond is :{rsp}"
            prompt += f"But the json data is not valid.\nError:{error} \nplease try again."
            rsp = self.llm_ask(prompt, system_prompt=system_prompt)
            json_data, error = parse_json_data(rsp)
            i += 1
        thoughts = rsp[: rsp.find("```json")] if rsp.find("```json") != -1 else rsp
        if json_data:
            command_list = parse_command(json_data, parse_type="json")
        thought_message = ThoughtMessage(
            send_to=agent_data.name,
            send_from=agent_data.name,
            content=rsp,
            time_stamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cause_by="MethodPlanAction",
            track=[f"file{__file__},line{inspect.currentframe().f_lineno}"],
        )
        agent_core = get_agent_core()
        agent_core.monitor.add_message(thought_message)
        return {"thoughts": thoughts, "action_command_list": command_list}

    @action()
    def finish_current_task(self):
        """Use this action to mark the current task as done.

        Args:
            task_description (str): The description of the new task"""
        agent_data = get_current_agent_data()
        plan_action_data = agent_data.get_action_data("MethodPlanAction")
        if len(plan_action_data.plan_list) > plan_action_data.current_plan_index:
            plan_action_data.plan_list[plan_action_data.current_plan_index]["status"] = "done"
            plan_action_data.current_plan_index += 1
        return "finish current task success."

    @action()
    def create_new_task(self, task_description: str):
        """Use this action to create a new task.

        Args:
            task_description (str): The description of the new task
        """
        agent_data = get_current_agent_data()
        plan_action_data = agent_data.get_action_data("MethodPlanAction")
        plan_action_data.plan_list.append({"description": task_description, "status": "TODO"})
        return "create new task success."

    @action()
    def wait_for_task(self):
        """If there is no task, take this action and wait for a new task."""
        agent_data = get_current_agent_data()
        agent_data.observe()
        agent_data.sleep()
        return ""

    @action()
    def end(self):
        """Use this action to stop. It is command when you do not recieve any useful command or do the final response."""
        agent_data = get_current_agent_data()
        agent_data.observe()
        agent_data.sleep()
        return ""

    def get_plan_list_description(self, plan_list):
        res = ""
        for index, plan in enumerate(plan_list):
            res += f"{index}.({plan['status']}) {plan['description']}\n"
        return res

    def init_agent(self, agent_data: AgentData):
        agent_data.set_action_data("MethodPlanAction", MethodPlanActionData())


def get_action():
    return MethodPlanAction()
