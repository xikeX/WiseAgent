from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction
from wiseagent.common.protocol_message import (
    EnvironmentHandleType,
    Message,
    UserMessage,
)
from wiseagent.env.base import BaseEnvironment


class CustomerEnvironmentHandleType(EnvironmentHandleType):
    CUSTOMER = "customer"


class CommunicaAction(BaseAction):
    @action()
    def respond_to_human(self, content):
        Message(send_to="user", content=content, env_handle_type=CustomerEnvironmentHandleType.CUSTOMER).send_message()
        return "[Action Respond] user receive message."


class CustomerEnvironment(BaseEnvironment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_message(self, message: Message):
        if message.env_handle_type == CustomerEnvironmentHandleType.CUSTOMER:
            # Do Customer action
            print(f"{message.send_from} said to {message.send_to} : {message.content}")

    def add_user_mesage(self, target_agent_name, content):
        """Add a user message to the environment and report it."""
        message = UserMessage(send_from="User", send_to=target_agent_name, content=content)
        self.env_report(message)


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Tom", action_list=[])
bob.register_action(CommunicaAction())
bob.life()
environment = CustomerEnvironment()
while True:
    content = input("User Message:")
    environment.add_user_mesage("Tom", content)
