import os

from wiseagent.core.agent import Agent
from wiseagent.core.agent_core import get_agent_core
from wiseagent.core.base_receiver import BaseReceiver
from wiseagent.env.multi_agent_env import MultiAgentEnv

data_yaml_folder = r"example\agent_yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    # load agent data
    agent_list = []
    for yaml_file in os.listdir(data_yaml_folder):
        agent_list.append(Agent.from_yaml_file(os.path.join(data_yaml_folder, yaml_file)))
    # start agent life
    for agent in agent_list:
        agent.life()

    env = MultiAgentEnv(use_stream=True)
    env._listen_user_input()


# @bob 写一个2048游戏
# @mike 搜索一下LLM,Agent,Social相关的文章，然后画出时间趋势图，按月来分，看每个月有多少篇。
# @mike 分析G:\WiseAgent_V3\WiseAgent\workspace\arxiv.json里面的论文，每一项是一个列表数据，其中第一条数据表示基本信息，比如"arXiv:2305.12815[pdf,other]",中2305表示23年5月，帮我按月份统计数量，并画出趋势图，你可以先看一下。
if __name__ == "__main__":
    main()
