from dataclasses import dataclass


@dataclass
class WebData:
    """
    Data class to hold the current state of the chat environment and agents.
    The chat environment and chat agent are exclusive; if one is changed, the other will be reset.
    """

    # Current active chat environment
    current_chat_enviornment = None
    environment_list = ["MultiAgentEnvironment"]
    # Current active chat agent. cur
    current_chat_agent = None
    agent_list = []  # [{"name":agent_name,"active":0/1}]
    # The agents file that has been loaded
    agent_yaml_file = []
