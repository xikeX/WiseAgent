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
    #     rsp = write_code_action.write_code(
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
# @bob 分析一下G:\Crop_Recommendation.csv"文件,分析的话，只需要读取前5条,这个是用一些土壤的数据，预测种植什么作物比较好。使用一个随机深林去预测，然后写一个streamlit 网页，能够输入一些土壤数据，然后输出预测结果。
# @bob “G:\WiseAgent_V3\WiseAgent\workspace\crop_prediction\app.py”读一下这个streamlit 的app.py 文件，这是一个利用土壤数据预测，种植什么作物比较好的数据集，请你美化界面，每一个参数要有英文说明。并且要求好用，不要有侧边栏。
# @bob "action_name": "WriteCodeAction", "action_method": "write_code",这个才是正确用法
# @Bob G:\Crop_Recommendation.csv"文件,可以先看一下前五条，这个是用一些土壤的数据，预测种植什么作物比较好的数据。你需要使用几种不同的方法去预测，然后写一个streamlit 网页，能够输入一些土壤数据，然后输出预测结果。这个网页包括3个tab页面，第一个tab页面是项目的说明；第二个tab页面是输入土壤数据：这个预测tab中，分为左右两部分，左边是输入土壤数据，右边是预测结果，需要有预测按钮，预测后给出最合适的农作物，和前3个合适作物的预测分数；第三个tab页面是预测结果，这个页面是数据分析界面，你需要分析原始数据的分布，给出一些分析用的图表。
# @Bob 之前预测的东西也要有。
if __name__ == "__main__":
    main()
