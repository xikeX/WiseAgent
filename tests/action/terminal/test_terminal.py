"""
Author: Huang Weitao
Date: 2024-10-23 20:33:27
LastEditors: Huang Weitao
LastEditTime: 2024-10-23 20:35:43
Description: 
"""

from wiseagent.action.normal_action.terminal import TerminalAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core

yaml_file = r"G:\WiseAgent_V3\WiseAgent\tests\action\terminal\agent.yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_data = AgentData.from_yaml_file(yaml_file)
    terminal = TerminalAction()
    terminal.init_agent(agent_data)
    with agent_data:
        while True:
            command = input()
            respond = terminal.run_command(command)
            print(respond)


if __name__ == "__main__":
    main()
