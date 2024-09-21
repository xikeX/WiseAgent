import time
from typing import List

from wiseagent.action.base_action import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.core.agent_core import get_agent_core
from wiseagent.life.life_scheduler.base_life_scheduler import BaseLifeScheduler
from wiseagent.protocol.action_command import ActionCommand


@singleton
class AutoStartLifeScheduler(BaseLifeScheduler):
    name: str = "AutoStartLifeScheduler"

    def __init__(self, life_scheduler):
        self.life_scheduler = life_scheduler

    def life(self):
        agent_data = get_current_agent_data()
        self.human_life(agent_data)

    def auto_start_mode(self, agent_data: "AgentData"):
        agent_core = get_agent_core()
        action_list = []
        for action_name in agent_data.action_ability:
            action = agent_core.get_action(action_name)
            action_list.append(action)
        while agent_data.is_alive:
            if agent_data.is_sleep:
                time.sleep(agent_data.heartbeat_interval)
                continue
            command_list: List[ActionCommand] = []
            action: BaseAction
            # Check Start
            rsp = ""
            for action in action_list:
                rsp += action.check_start(agent_data, command_list=command_list)
            agent_data.add_memory(rsp)
            # Act
            for command in command_list:
                action = agent_core.get_action(command.action_name)
                if hasattr(action, command.action_method) and callable(getattr(action, command.action_method)):
                    action_method = getattr(action, command.action_method)
                    rsp = action_method(agent_data, command)
                else:
                    rsp = f"{command.action_method} not found"
                agent_data.add_memory(command.action_name, rsp)


def get_life_scheduler():
    return AutoStartLifeScheduler()
