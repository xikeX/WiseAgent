"""
Author: Huang Weitao
Date: 2024-09-30 00:08:48
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:37:48
Description: Run arxiv agent
"""
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv

yaml_file = r"tests\run\run_arxiv_agent\arxiv_agent.yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_core._preparetion()
    # load agent data
    agent_data_list = []
    agent_data_list.append(AgentData.from_yaml_file(yaml_file))
    # init agent
    for agent_data in agent_data_list:
        agent_core.init_agent(agent_data)
    # start agent life
    for agent_data in agent_data_list:
        agent_core.start_agent_life(agent_data)
    # run env
    env = MultiAgentEnv()
    env._listen_user_input()


# @Bob 收集一下包含LLM和Agent的论文，最近7天的，保存起来，名字就叫‘LLM_Agent 2024-10-03 2024-10-10.xlsx’
if __name__ == "__main__":
    main()
