import asyncio
import logging
import threading
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.core.agent import get_current_agent_data

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """
        connect to mcp server, and keep the connection alive
        Args:
            server_script_path: the path of the server script
        """
        server_script_path = server_script_path.strip()
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        is_node = server_script_path.startswith("@")
        assert is_python or is_js or is_node, "server_script_path must be a python script, a js script or a node script"
        if is_node:
            server_params = StdioServerParameters(command="npx", args=["-y", server_script_path], env=None)
        elif is_python:
            server_params = StdioServerParameters(command="python", args=[server_script_path], env=None)
        elif is_js:
            server_params = StdioServerParameters(command="node", args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        logger.info(f"Available tools: {tools}")

    async def get_available_tools(self):
        return await self.session.list_tools()

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        logger.info(f"Calling tool {tool_name} with args {tool_args}")
        result = await self.session.call_tool(tool_name, tool_args)
        return result.content[0].text

    async def close(self):
        await self.stdio.close()
        await self.exit_stack.aclose()


class SyncMCPClient:
    def __init__(self):
        self.client = MCPClient()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_coroutine(self, coro):
        """在异步线程中运行协程"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()  # 同步等待结果

    def connect_to_server(self, server_script_path: str):
        self._run_coroutine(self.client.connect_to_server(server_script_path))

    def call_tool(self, tool_name: str, tool_args: dict):
        return self._run_coroutine(self.client.call_tool(tool_name, tool_args))

    def get_available_tools(self):
        return self._run_coroutine(self.client.get_available_tools())

    def close(self):
        self._run_coroutine(self.client.close())
        self.loop.call_soon_threadsafe(self.loop.stop)


class MCPDataClass(BaseActionData):
    client: Any = None
    tool_list: List = []

    def __init__(self, server_script_path: Any):
        super().__init__()
        self.client = SyncMCPClient()
        self.client.connect_to_server(server_script_path)
        self.tool_list = self.client.get_available_tools().tools


class MCPAction(BaseAction):
    "use MCP tools to process queries"

    def __init__(self):
        super().__init__()
        # 在这里并不能知道智能体能够使用什么特定的工具

    def init_agent(self, agent_data):
        action_data_config = agent_data.get_action_config(self.action_name)
        mcp_data = MCPDataClass(server_script_path=action_data_config["server_script_path"])
        agent_data.set_action_data(self.action_name, mcp_data)
        # 在初始化的时候告诉智能体有什么工具
        if "class_methods" not in self.action_description:
            self.action_description["class_methods"] = {}
        for tool in mcp_data.tool_list:
            self.action_description["class_methods"][tool.name] = {
                "description": tool.description,
                "params": [f"{name}({p['type']})" for name, p in tool.inputSchema["properties"].items()],
            }

    # @action()
    # def call_tool(self, tool_name: str, tool_args: dict):
    #     """Execute a tool with the given name and arguments
    #     Args:
    #         tool_name (str): The name of the tool to execute
    #         tool_args (dict): The arguments to pass to the tool
    #     """
    #     agent_data = get_current_agent_data()
    #     mcp_data_class:MCPDataClass = agent_data.get_action_data(self.action_name)
    #     return mcp_data_class.client.call_tool(tool_name, tool_args)
    def __getattr__(self, name):
        """when calling mcp methods, but the method is not defined in this class, then call the method in mcp_data_class"""
        agent_data = get_current_agent_data()
        if name not in self.action_description["class_methods"]:
            return f"Method {name} not found in MCPAction"

        def method(**kwargs):
            return agent_data.get_action_data(self.action_name).client.call_tool(name, kwargs)

        return method

    # @action()
    # def get_avalible_tools(self):
    #     """Get a list of available tools"""
    #     agent_data = get_current_agent_data()
    #     mcp_data:MCPDataClass = agent_data.get_action_data(self.action_name)
    #     return mcp_data.tool_list


def get_action():
    return MCPAction()
