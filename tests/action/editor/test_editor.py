"""
Author: Huang Weitao
Date: 2024-10-23 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-10-23 14:24:14
Description:  
"""
from wiseagent.action.normal_action.editor import EditorAction
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core

yaml_file = r"G:\WiseAgent_V3\WiseAgent\tests\action\long_document_generate\agent.yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_data = AgentData.from_yaml_file(yaml_file)
    editor = EditorAction()
    editor.init_agent(agent_data)
    with agent_data:
        respond = editor.read_excel(r"G:\WiseAgent_V3\WiseAgent\workspace\arxiv_papers.xlsx", limit=10)
        print(respond)


if __name__ == "__main__":
    main()
