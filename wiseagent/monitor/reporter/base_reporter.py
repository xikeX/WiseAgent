'''
Author: Huang Weitao
Date: 2024-09-17 14:23:42
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 18:38:57
Description: 
'''

from pydantic import BaseModel
from abc import ABC,abstractmethod

from wiseagent.agent_data.base_agent_data import AgentData

class BaseReporter(BaseModel,ABC):
    """
    Base class for all reporters
    """
    name = "base_reporter"
    @abstractmethod
    def report(self,agentdata:"AgentData", report_type,report_data):
        """
        Report data to the reporter
        """
        raise NotImplementedError