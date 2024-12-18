from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction
from wiseagent.common.protocol_message import (
    EnvironmentHandleType,
    Message,
    UserMessage,
)
from wiseagent.common.singleton import singleton
from wiseagent.env.base import BaseEnvironment


class CustomerEnvironmentHandleType(EnvironmentHandleType):
    CUSTOMER = "customer"


class CustomerEnvironment(BaseEnvironment):
    agent_list: list = []

    def __init__(self, agent_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_list = agent_list

    def handle_message(self, message: Message):
        if message.env_handle_type == CustomerEnvironmentHandleType.CUSTOMER:
            # Do Customer action
            if message.send_to in self.agent_list:
                # transfer to other agent
                message.content = f"from {message.send_from} to {message.send_to} message:{message.content}"
                self.env_report(message)
            else:
                print(f"from {message.send_from} to {message.send_to} message:{message.content}")

    def add_user_mesage(self, target_agent_name, content):
        """Add a user message to the environment and report it."""
        message = UserMessage(send_from="User", send_to=target_agent_name, content=content)
        self.env_report(message)


@singleton
class CommunicaAction(BaseAction):
    @action()
    def respond(self, send_to, content):
        Message(send_to=send_to, content=content, env_handle_type=CustomerEnvironmentHandleType.CUSTOMER).send_message()
        return "[Action Respond] send message successfully."


environmet_description = """
There are three roles in this environment:
1. user
2. bob
3. alice
""".strip()
from wiseagent.core.agent import Agent

bob = Agent.from_default(name="bob", action_list=[], current_environment=environmet_description)
bob.register_action(CommunicaAction())
bob.life()
alice = Agent.from_default(name="alice", action_list=[], current_environment=environmet_description)
alice.register_action(CommunicaAction())
alice.life()
environment = CustomerEnvironment(agent_list=["tom", "alice"])
while True:
    content = input("User Message:(role:message)")
    role, content = content.split(":", 1)
    environment.add_user_mesage(role, content)
