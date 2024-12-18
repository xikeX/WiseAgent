from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction


class MyAction(BaseAction):
    @action()
    def report_to_user(self, content):
        """
        report to the user
        Args:
            content: the content to report
        """
        print("AI :", content)
        return "report success"


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob", action_list=[])  # Set action_list to []
bob.register_action(MyAction())  # register customer action
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
