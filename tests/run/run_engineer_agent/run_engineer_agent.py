"""
Author: Huang Weitao
Date: 2024-09-30 00:08:48
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:37:48
Description: Run arxiv agent
"""
from wiseagent.action.normal_action.write_code import WriteCodeAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv

yaml_file = r"tests\run\run_engineer_agent\engineer_agent.yaml"


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
    # with agent_data_list[0]:
    #     write_code_action = WriteCodeAction()
    #     rsp = write_code_action.wirte_code(
    #         file_list=[
    #             "2048_game/index.html",
    #             "2048_game/main.js",
    #             "2048_game/style.css",
    #         ],
    #         file_description="完成一个2048游戏 2048_game/index.html实现页面 2048_game/main.js实现游戏逻辑 2048_game/style.css实现页面样式"
    #     )
    #     logger.info(rsp)
    #     rsp = write_code_action.open_html("2048_game/index.html")
    #     logger.info(rsp)


# @Bob 完成一个2048游戏
# @bob 完成一个贪吃蛇游戏
# @bob 写一个万年历，要界面美观。
# @bob 写一个五子棋游戏
# @bob 写一个井字棋游戏网页
# @bob 俄罗斯方块游戏，并运行
# @bob 实现一个flappy bird 游戏
# @bob 实现一个扫雷游戏
# @bob 写一个计算器，要求涵盖常见所有的运算，并且界面美观。
# @bob 写一个登录界面，要求界面美观，并且实现登录功能。
if __name__ == "__main__":
    main()
