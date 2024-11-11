"""
Author: Huang Weitao
Date: 2024-09-19 23:37:08
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 02:08:04
Description: 
"""
from typing import Dict, List

from pydantic import BaseModel


class Command(BaseModel):
    command_name: str = ""
    cause_by: str = ""


class ActionCommand(Command):
    action_name: str = ""
    action_method: str = ""
    args: Dict = {}

    def to_dict(self):
        return {
            "command_name": self.command_name,
            "cause_by": self.cause_by,
            "action_name": self.action_name,
            "action_method": self.action_method,
            "args": self.args,
        }


def parse_command(data: List[Dict]):
    command_list = []
    for command in data:
        command_list.append(ActionCommand(**command))
    return command_list
