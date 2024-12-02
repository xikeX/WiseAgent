"""
Author: Huang Weitao
Date: 2024-09-21 19:19:27
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 20:16:33
Description: 
"""
import json
from typing import Dict, List

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseActionData, BasePlanAction
from wiseagent.common.parse_llm_respond import parse_command_xml_data, parse_json_data
from wiseagent.common.protocol_command import ActionCommand, parse_command
from wiseagent.common.protocol_message import (
    CreateTaskMessage,
    FinishTaskMessage,
    ThoughtMessage,
)
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data

JSON_INSTRUCTION_PROMPT = """
## Plan List
{plan_list}
## Current Task
{current_task}
## Instruction
Please generate a plan for the agent to complete the task.
Your respond must contain the thought and a json for action command list.
If the task has been completed, use action_name:"MethodPlanAction" and use the action_method:"end" to stop
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
If the task has been completed, use action_name:"MethodPlanAction" and use the action_method:"end" to stop
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

    def __init__(self, agent_data: Agent):
        super().__init__()

        # Initialize the data from action_config
        action_config = agent_data.get_action_config(
            "MethodPlanAction",
        ) or {"parse_type": "xml", "expericence": None}
        self.parse_type = action_config.get("parse_type", None) or "xml"
        self.expericence = action_config.get("expericence", None) or JSON_EXPERIENCE

        # Select the instruction prompt
        if self.parse_type == "json":
            self.instruction_prompt = JSON_INSTRUCTION_PROMPT
        else:
            self.instruction_prompt = XML_INSTRUCTION_PROMPT


@singleton
class MethodPlanAction(BasePlanAction):
    """The planner of the agent, which is used to plan the action of the agent"""

    max_tries: int = 3
    parse_function: dict = {}

    def __init__(self):
        super().__init__()
        self.parse_function = {"json": parse_json_data, "xml": parse_command_xml_data}

    def init_agent(self, agent_data: Agent):
        agent_data.set_action_data("MethodPlanAction", MethodPlanActionData(agent_data))

    def plan(self, command_list: List[ActionCommand]) -> Dict:
        """Execute the plan action
        Args:
            command_list (List[ActionCommand]): The command list of the agent

        Returns:
            Dict: The result of the plan action, which may include thoughts, action command list, etc.
        """
        agent_data: Agent = get_current_agent_data()
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
            command_data, error = self.parse_function[plan_action_data.parse_type](rsp)
            prompt = instruction_prompt + f"Your respond is :{rsp}"
            prompt += f"But the data format is not valid.\nError:{error} \nplease try again."
            i += 1
        thoughts = (
            rsp[: rsp.find(f"```{plan_action_data.parse_type}")]
            if rsp.find(f"```{plan_action_data.parse_type}") != -1
            else rsp
        )
        if command_data:
            command_list = parse_command(command_data)
        ThoughtMessage(
            content=json.dumps([c.to_dict() for c in command_list], ensure_ascii=False), cause_by="MethodPlanAction"
        ).send_message()
        return {"thoughts": thoughts, "action_command_list": command_list}

    @action()
    def finish_current_task(self, task_id, task_description):
        """Use this action to mark the current task as done.
        Args:
            task_id(int): The id of the task to be finished.
            task_description (str): The description of the new task.
        """
        agent_data = get_current_agent_data()
        plan_action_data = agent_data.get_action_data("MethodPlanAction")
        if task_id < len(plan_action_data.plan_list):
            plan_action_data.plan_list[task_id]["status"] = "done"
            current_plan_index = plan_action_data.current_plan_index
            FinishTaskMessage(
                content=json.dumps(
                    {
                        "task_id": task_id,
                        "description": plan_action_data.plan_list[task_id]["description"],
                        "status": "done",
                    }
                )
            ).send_message()
            while (
                plan_action_data.current_plan_index < len(plan_action_data.plan_list)
                and plan_action_data.plan_list[current_plan_index]["status"] == "done"
            ):
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
        task_id = len(plan_action_data.plan_list)
        plan_action_data.plan_list.append({"task_id": task_id, "description": task_description, "status": "TODO"})
        CreateTaskMessage(
            content=json.dumps({"task_id": task_id, "description": task_description, "status": "TODO"})
        ).send_message()
        return f"create new task success. Task Id:{task_id}"

    @action()
    def wait_for_task(self):
        """If there is no task, take this action and wait for a new task."""
        self.end()

    @action()
    def wait_for_response(self):
        """If there is no task, take this action and wait for a new respond."""
        self.end()

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
