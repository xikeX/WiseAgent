from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction, BaseActionData


class MemoActionData(BaseActionData):
    memo: list[str] = []


class MemoAction(BaseAction):
    def init_agent(self, agent_data):
        self.set_action_data(agent_data, data=MemoActionData())

    @action()
    def record(self, content):
        """
        Record the content to record.
        The content only contain one thing.
        Args:
            content: the record item.
        """
        memo_action_data = self.get_action_data()
        memo_action_data.memo.append(content)
        print(f"Add {content} to memo.")
        return f"Add {content} to memo successfully."

    @action()
    def list_memo(self):
        """
        List the item in the memo
        """
        memo_action_data = self.get_action_data()
        record = "\n".join([str(i) + "." + content for i, content in enumerate(memo_action_data.memo)])
        return record


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob")
bob.register_action(MemoAction())  # register customer action
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
