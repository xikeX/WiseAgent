'''
Author: Huang Weitao
Date: 2024-09-17 14:23:53
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 14:46:02
Description: 
'''

from pydantic import BaseModel


class BaseAction(BaseModel):
    action_name: str
    action_type: str
    action_description: str
    