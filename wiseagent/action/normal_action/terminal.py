"""
Author: Huang Weitao
Date: 2024-10-23 20:24:01
LastEditors: Huang Weitao
LastEditTime: 2024-10-23 20:37:23
Description: 
"""
from typing import Any

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.tools.terminal_tool import TerminalTool


class TerminalActionData(BaseActionData):
    terminal_tool: Any = TerminalTool()


@singleton
class TerminalAction(BaseAction):
    action_description: str = "Terminal action"

    def init_agent(self, agent_data: Agent):
        agent_data.set_action_data(self.action_name, TerminalActionData())

    def get_termianl(self):
        agent_data = get_current_agent_data()
        terminal_tool = agent_data.get_action_data(self.action_name).terminal_tool
        return terminal_tool

    @action()
    def run_command(self, terminal_command: str):
        """Execute terminal command

        Args:
            terminal_command (str): Terminal command to execute
        """
        terminal_tool: TerminalTool = self.get_termianl()
        result = terminal_tool.run_command(terminal_command)
        return f"[Observed]:\n{terminal_command} executed with result:\n{result}\n[End Observed]"

    @action()
    def read_terminal(self):
        """Read terminal content

        Returns:
            str: Terminal content
        """
        terminal_tool: TerminalTool = self.get_termianl()
        result = terminal_tool.read_terminal()
        return f"[Observed]:\n{result}\n[End Observed]"


def get_action():
    return TerminalAction()
