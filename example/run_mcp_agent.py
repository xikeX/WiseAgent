from wiseagent.action.normal_action.mcp_action import MCPAction
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
    mcp_agent = Agent.from_default(name="Bob", description="Bob is a engineer")
    # 注册一个动作/工具
    mcp_agent.set_action_config("MCPAction",{"server_script_path":r"@executeautomation/playwright-mcp-server"})
    mcp_action = MCPAction()
    mcp_action.init_agent(mcp_agent)

    mcp_agent.register_action(mcp_action)

    # 让智能体开始工作
    mcp_agent.life()
    # 获取用户输入并执行动作
    get_user_input(mcp_agent)


if __name__ == "__main__":
    main()
