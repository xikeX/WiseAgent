"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-09-20 00:25:11
Description: 
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from wiseagent.common.annotation import singleton


@singleton
class BaseLifeScheduler(BaseModel, ABC):
    """Base class for all life schedules"""

    name: str = ""

    @abstractmethod
    def life(self):
        pass
