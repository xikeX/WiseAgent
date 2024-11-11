"""
Author: Huang Weitao
Date: 2024-09-26 22:39:16
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 20:12:24
Description: 
"""
from wiseagent.core.agent import Agent

# yaml_file = r"example\agent_yaml\chat_agent.yaml"
yaml_file = r"example\agent_yaml\arxiv_agent.yaml"
# yaml_file = r"example\agent_yaml\document_generate_agent.yaml"
# yaml_file = r"example\agent_yaml\engineer_agent.yaml"
# yaml_file = r"example\agent_yaml\wechat_agent.yaml"


def get_user_input(agent):
    while True:
        user_input = input("Please input your task:")
        if user_input == "exit":
            break
        # 让智能体根据用户输入执行动作
        agent.ask(user_input)


def main():
    agent: Agent = Agent.from_yaml_file(yaml_file)
    # 让智能体开始工作
    agent.life()
    # 获取用户输入并执行动作
    get_user_input(agent)


if __name__ == "__main__":
    main()
