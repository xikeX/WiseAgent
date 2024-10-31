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
from wiseagent.common.parse_llm_respond import parse_json_data, parse_xml_data
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.action_command import ActionCommand, parse_command
from wiseagent.protocol.message import ThoughtMessage

JSON_INSTRUCTION_PROMPT = """
## Plan List
{plan_list}
## Current Task
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
JSON_EXPERIENCE = """
output format:
[
    {
        "action_name": "Chat",
        "action_method" : "chat",
        "args": {
            "agrs_name": "args_value",
            ...
        }
    }
]
"""

XML_INSTRUCTION_PROMPT = """
## Plan List
{plan_list}
## Current Task
{current_task}
## Instruction
Please generate a plan for the agent to complete the task.
Your respond must contain the thought and a xml for action command list.
The xml format is:
```xml
<action_list>
<action>
<action_name>action_name</action_name>
<action_method>action_method</action_method>
<args name="arg_name_1" type = str >arg_value_1</args>
<args name="arg_name_2" type = list >[arg_value_2]</args>
<args name="arg_name_3" type = int >arg_value_3</args>
...
</action>
...
</action_list>
```
"""
XML_EXPERIENCE = """
output format:
<action_list>
<action>
<action_name>Chat</action_name>
<action_method>chat</action_method>
<args name="send_to" type = str >Alice</args>
<args name="message" type = str >Hello, Alice!</args>
</action>
...
</action_list>
"""


class MethodPlanActionData(BaseActionData):
    """The data of the method plan action"""

    instruction_prompt: str = ""
    expericence: str = ""
    plan_list: List[dict] = []
    current_plan_index: int = 0
    parse_type: str = "xml"
    instruction_prmeompt: str = ""

    def __init__(self, agent_data: AgentData):
        super().__init__()
        # if agent_data has experience, use it, otherwise use the default experience
        if hasattr(agent_data, "parse_type"):
            self.parse_type = agent_data.parse_type or "xml"
        if self.parse_type == "json":
            self.instruction_prompt = JSON_INSTRUCTION_PROMPT
            self.expericence = agent_data.get_experience("MethodPlanAction") or JSON_EXPERIENCE
        else:
            self.instruction_prompt = XML_INSTRUCTION_PROMPT
            self.expericence = agent_data.get_experience("MethodPlanAction") or XML_EXPERIENCE
        pass


@singleton
class MethodPlanAction(BasePlanAction):
    """The planner of the agent, which is used to plan the action of the agent"""

    action_name: str = "MethodPlan"
    max_tries: int = 3
    parse_json_data: dict = {}
    parse_function: dict = {}

    def __init__(self):
        super().__init__()
        self.parse_function = {"json": parse_json_data, "xml": parse_xml_data}

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
        i, error = 0, "start"
        while error and i < self.max_tries:
            rsp = self.llm_ask(instruction_prompt, system_prompt=system_prompt)
            json_data, error = self.parse_function[plan_action_data.parse_type](rsp)
            prompt = instruction_prompt + f"Your respond is :{rsp}"
            prompt += f"But the data format is not valid.\nError:{error} \nplease try again."
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
    def finish_current_task(self, task_description):
        """Use this action to mark the current task as done.

        Args:
            task_description (str): The description of the new task"""
        agent_data = get_current_agent_data()
        plan_action_data = agent_data.get_action_data("MethodPlanAction")
        if len(plan_action_data.plan_list) > plan_action_data.current_plan_index:
            plan_action_data.plan_list[plan_action_data.current_plan_index]["status"] = "done"
            plan_action_data.current_plan_index += 1
        return "Finish current task success."

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
        agent_data.set_action_data("MethodPlanAction", MethodPlanActionData(agent_data))


def get_action():
    return MethodPlanAction()
