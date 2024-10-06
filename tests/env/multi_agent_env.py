"""
Author: Huang Weitao
Date: 2024-09-26 22:39:16
LastEditors: Huang Weitao
LastEditTime: 2024-09-27 09:01:34
Description: 
"""


import os

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv
from wiseagent.receiver.base_receiver import BaseReceiver

data_yaml_folder = r"tests\env\agent_data_yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_core._preparetion()
    # load agent data
    yaml_list = os.listdir(data_yaml_folder)
    agent_data_list = []
    for yaml_file in yaml_list:
        agent_data_list.append(AgentData.from_yaml_file(os.path.join(data_yaml_folder, yaml_file)))
    # init agent
    for agent_data in agent_data_list:
        agent_core.init_agent(agent_data)
    # start agent life
    for agent_data in agent_data_list:
        agent_core.start_agent_life(agent_data)
    # run env
    env = MultiAgentEnv()
    env._listen_user_input()


if __name__ == "__main__":
    main()
