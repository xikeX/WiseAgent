"""
Author: Huang Weitao
Date: 2024-09-19 23:37:08
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 02:08:04
Description: 
"""
from typing import Dict

from pydantic import BaseModel


class Command(BaseModel):
    command_name: str = ""
    cause_by: str = ""


class ActionCommand(Command):
    action_name: str = ""
    action_method: str = ""
    parameters: Dict = {}
