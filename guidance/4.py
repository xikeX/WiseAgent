from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction


class GenerateArticle(BaseAction):
    @action()
    def generate_article(self, topic, language):
        """
        generate article
        Args:
            topic: the topic of the article.
            language: the language that article write in.
        """
        # 1. generate outline
        prompt_1 = f"##Topic\n{topic}\n## Instruction\nplease generate a outline of the topic in {language}"
        outline = self.llm_ask(prompt_1, memory=[], system_prompt="")
        print("outline", outline)
        prompt_2 = f"##Topic\n{topic}\n##Outline\n{outline}\n##Instruction\nplease generate a article in {language} based on the topic and outline."
        article = self.llm_ask(prompt_2, memory=[], system_prompt="")
        print("article", article)
        return "article genrate successfully"


from wiseagent.core.agent import Agent

bob = Agent.from_default(name="Bob")
bob.register_action(GenerateArticle())  # register customer action
bob.life()
while True:
    message = input("User Massage:")
    bob.input(message)
