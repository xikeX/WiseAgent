
from pydantic import BaseModel
from wiseagent.common.annotation import singleton

@singleton
class BaseLifeScheduler(BaseModel,ABC):
    """Base class for all life schedules"""
    name
    pass
    @abstractclassmethod
    def life(self):
        pass