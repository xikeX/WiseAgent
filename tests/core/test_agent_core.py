import pytest
from wiseagent.core.agent_core import AgentCore,get_agent_core

@pytest.fixture
def agent_core():
    return AgentCore()

def test_get_agent_core():
    agent_core = AgentCore()
    assert isinstance(agent_core, AgentCore)