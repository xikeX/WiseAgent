from wiseagent.action.base_action import BasePlanAction
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.core.agent import Agent, get_current_agent_data

THINK = """Answer the following question tree question:
1. What is your task?
2. What is your observation?
3. What you need to do next？
"""
PLAN = """
## Your Thought
{thought}

## Instructions
Give out an action according your thought in the following format:
Class: the class name of the action
Method: the method name of the action
parameter_name_1: the first parameter of the action, if exists
parameter_name_2: the second parameter of the action, if exists
...
"""


class ThinkPlan(BasePlanAction):
    def plan(self, command_list):
        agent: Agent = get_current_agent_data()
        # 1.Think
        think_prompt = THINK
        system_prompt = agent.get_agent_system_prompt()
        thought = self.llm_ask(think_prompt, system_prompt=system_prompt)
        # 2. Plan
        for _ in range(3):
            try:
                plan_prompt = PLAN.format(thought=thought)
                respond = self.llm_ask(plan_prompt, system_prompt=system_prompt)
                command = self.parse_command(respond)
                command_list.append(command)
                break
            except Exception as e:
                print(e)
                continue
        return thought, command_list

    def parse_command(self, respond):
        """parse llm response to command"""
        class_name = ""
        class_method = ""
        parameters = {}
        for line in respond.split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key == "Class":
                class_name = value
            elif key == "Method":
                class_method = value
            else:
                parameters[key] = value
        if class_name == "" or class_method == "":
            raise ValueError("Invalid command format")
        return ActionCommand(action_name=class_name, action_method=class_method, args=parameters)


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob", default_plan=None, agent_instructions="用中文回复")
bob.register_action(ThinkPlan())  # register customer action
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
