
from pydantic import BaseModel
from wiseagent.agent_data.base_agent_data import AgentData

from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core


@singleton
class ReActLifeSchedule(BaseModel):
    def __init__(self, life_manager):
        self.life_manager = life_manager

    def react(self,agent_data:"AgentData"):
        agent_core = get_agent_core(agent_data)
        # select the plan action and normal action of the agent
        plan_action = []
        normal_action = []
        for action_name in agent_data.action_ability:
            action = agent_core.get_action(action_name)
            if isinstance(action, PlanAction):
                plan_action.append(action)
            else:
                normal_action.append(action)

        while agent_data.is_alive:
            # Observe
            # Because the message will automatically add to the short_term memory, so we don't need to add it manually
            
            # Plan
            
            # Act
        pass