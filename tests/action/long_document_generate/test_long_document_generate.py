"""
Author: Huang Weitao
Date: 2024-10-14 00:03:57
LastEditors: Huang Weitao
LastEditTime: 2024-10-14 00:07:19
Description: 
"""
from wiseagent.action.normal_action.long_document_generate import (
    LongDocumentGenerateAction,
)
from wiseagent.agent_data.base_agent_data import AgentData
from wiseagent.core.agent_core import get_agent_core
from wiseagent.env.multi_agent_env import MultiAgentEnv

yaml_file = r"G:\WiseAgent_V3\WiseAgent\tests\action\long_document_generate\agent.yaml"


def main():
    agent_core = get_agent_core()
    agent_core.init()
    agent_data = AgentData.from_yaml_file(yaml_file)
    long_document_generate = LongDocumentGenerateAction()
    long_document_generate.init_agent(agent_data)
    with agent_data:
        outline = long_document_generate.generate_outline(
            topic="React 前端 入门指南",
            description="React 是一个用于构建用户界面的 JavaScript 库，它可以帮助开发者构建出高性能、可维护的 web 应用。本指南将介绍 React 的基本概念、使用方法以及一些高级技巧，帮助初学者快速入门 React 前端开发。",
            language="中文",
        )
        respond = long_document_generate.create_long_document(
            topic="React 前端 入门指南",
            outline=outline,
            description="React 是一个用于构建用户界面的 JavaScript 库，它可以帮助开发者构建出高性能、可维护的 web 应用。本指南将介绍 React 的基本概念、使用方法以及一些高级技巧，帮助初学者快速入门 React 前端开发。",
            language="中文",
            save_path="React 前端 入门指南.md",
        )
        print(respond)


if __name__ == "__main__":
    main()
