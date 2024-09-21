from typing import Dict, List

from wiseagent.action.action_annotation import action
from wiseagent.action.plan_action.base_plan_action import BasePlanAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.common.annotation import singleton
from wiseagent.protocol.action_command import ActionCommand


@singleton
class MethodPlanAction(BasePlanAction):
    """The planner of the agent, which is used to plan the action of the agent"""

    def __init__(self, method_name, method):
        self.method_name = method_name
        self.method = method

    @action()
    def plan(self, a: int) -> Dict:
        """Execute the plan action
        Args:
            **kwargs: Additional arguments, which can be used by the plan action

        Returns:
            Dict: The result of the plan action, which may include thoughts, action command list, etc.
        """
        # 1. Get the method description of the agent


def get_action():
    return MethodPlanAction()
