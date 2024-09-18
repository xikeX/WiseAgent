
class LifeScheduler:
    """
    Base class for life schedulers
    """

    def __init__(self, config):
        self.config = config

    def schedule(self, life):
        """
        Schedule a life
        """
        raise NotImplementedError("schedule method not implemented")