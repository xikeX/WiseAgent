'''
Author: Huang Weitao
Date: 2024-09-19 23:37:08
LastEditors: Huang Weitao
LastEditTime: 2024-09-19 23:39:15
Description: 
'''
from pydantic import BaseModel

class Command(BaseModel):
    command_name = ""
    cause_by = ""
    

class ActionCommand(Command):
    comman_parameters = {}