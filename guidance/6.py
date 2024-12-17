import json

from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.protocol_message import AIMessage
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.life_scheduler.base_life_scheduler import BaseLifeScheduler


class CustomerLifeScheduler(BaseLifeScheduler):
    def life(self):
        from wiseagent.core.agent import Agent, get_current_agent_data

        agent: Agent = get_current_agent_data()
        agent_core = get_agent_core()
        plan_action = self.get_agent_plan_action(agent)[0]
        while agent.is_alive:
            # 0. wait for new message
            if not agent.is_activate:
                agent.wait_for_new_message()

            # new_message = agent.get_latest_memory(1)[0]
            # 1. make plan
            command_list = []
            thought, command_list = plan_action.plan(command_list)
            if thought:
                agent.add_memory(AIMessage(content=thought))
            if command_list:
                agent.add_memory(AIMessage(content=json.dumps([i.to_dict() for i in command_list])))
            # 2. execute plan
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
                    agent.add_memory(AIMessage(content=rsp))
            # 3. set is_activate to False, wait for new message
            agent.is_activate = False


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob", agent_instructions="用中文回复", life_schedule_config="CustomerLifeScheduler")
bob.register_life_scheduler(CustomerLifeScheduler())
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
