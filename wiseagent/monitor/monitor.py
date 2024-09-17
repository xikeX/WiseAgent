'''
Author: Huang Weitao
Date: 2024-09-17 14:23:28
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 18:44:05
Description: 
'''

from typing import List
from typing_extensions import Unpack

from pydantic import BaseModel, ConfigDict
from wiseagent.monitor.reporter.base_reporter import BaseReporter


class Monitor(BaseModel):
    report: List[BaseReporter] = []
    # TODO: add more fields as needed
    
    def __init_subclass__(cls, **kwargs: *ConfigDict):
        return super().__init_subclass__(**kwargs)