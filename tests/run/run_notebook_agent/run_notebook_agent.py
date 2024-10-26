"""
Author: Huang Weitao
Date: 2024-10-20 14:47:34
LastEditors: Huang Weitao
LastEditTime: 2024-10-20 15:00:12
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-26 22:39:16
LastEditors: Huang Weitao
LastEditTime: 2024-09-28 20:12:24
Description: 
"""


import os

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv
from wiseagent.receiver.base_receiver import BaseReceiver

yaml_file = r"F:\WiseAgent\WiseAgent\tests\run\run_notebook_agent\agent.yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
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


# @Jusep 分析一下鸢尾花数据集

if __name__ == "__main__":
    main()
