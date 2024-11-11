"""
Author: Huang Weitao
Date: 2024-11-09 17:44:51
LastEditors: Huang Weitao
LastEditTime: 2024-11-09 19:05:21
Description: 
"""
from wiseagent.action.normal_action.write_code import WriteCodeAction
from wiseagent.core.agent import Agent


def get_user_input(engineer):
    while True:
        user_input = input("Please input your task:")
        if user_input == "exit":
            break
        # 让智能体根据用户输入执行动作
        engineer.ask(user_input)


def main():
    # 创建一个智能体
    engineer = Agent.from_default(name="Bob", description="Bob is a engineer")
    # 注册一个动作/工具
    engineer.register_action(WriteCodeAction())
    # 让智能体开始工作
    engineer.life()
    # 获取用户输入并执行动作
    get_user_input(engineer)


if __name__ == "__main__":
    main()
