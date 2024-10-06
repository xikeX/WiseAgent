from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv


class MultiAgentEnvServer:
    agent_yaml_string: list[str] = []
    env: None
    agent_name_list: list[str] = []

    def __init__(self) -> None:
        """The agent_core is singleton. In oder to ignore circle import, we use this way to get agent_core."""
        agent_core = get_agent_core()
        agent_core.init()
        agent_core._preparetion()
        # run env
        self.env = MultiAgentEnv()
        self.message_cache = self.env.message_cache

    def add_agent(self, yaml_string):
        if yaml_string in self.agent_yaml_string:
            return False, "agent already exist"
        self.agent_yaml_string.append(yaml_string)
        agent_data = AgentData.from_yaml_string(yaml_string)
        self.agent_name_list.append(agent_data.name.lower())
        agent_core = get_agent_core()
        agent_core.init_agent(agent_data)
        agent_core.start_agent_life(agent_data)
        self.env.add_agent(agent_data.name)
        return True, "add agent success"

    def post_message(self, target_agent_name, content):
        if target_agent_name not in self.agent_name_list:
            return False, "agent not exist"
        self.env.add_user_mesage(target_agent_name, content)
        return True, "post message success"

    def get_message(self, position_tag: int):
        """
        Args:
            position_tag (int): the position of the sending message in the message_cache

        Returns:
            tuple: (message,next_position_tag,has_next)
        """
        if position_tag >= len(self.message_cache):
            return None, None, position_tag, False
        return self.message_cache[position_tag][0], self.message_cache[position_tag][1], position_tag + 1, True
        #  this will be loop for frontend to get the newest message

    def get_agent_list(self):
        return self.agent_name_list


def create_app(run_mode: str = None):
    app = FastAPI(
        title="Langchain-Chatchat API Server",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
