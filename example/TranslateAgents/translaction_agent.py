from customer_actions.translate_actions import TranslateAction

from wiseagent.core.agent import Agent


def main():
    translator = Agent.from_default(
        name="Alex",
        action_list=[],
    )
    translate_action = TranslateAction()
    translator.register_action(translate_action)
    translator.life()
    while True:
        message = ""
        in_p = input("Send a message to Alex:")
        while in_p != "end":
            message += in_p
            in_p = input("Send a message to Alex:")
        translator.input(message)


if __name__ == "__main__":
    main()

"""
将小说翻译为中文：
小说文件路径是noval.txt
end
"""
