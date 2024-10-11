"""
Author: Huang Weitao
Date: 2024-10-05 00:38:39
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 17:37:43
Description: 
"""

import uvicorn

from wiseagent.common.file_io import read_rb
from wiseagent.protocol.message import EnvironmentHandleType, FileUploadMessage, Message
from wiseagent.server.multi_agent_env_server import MultiAgentEnvServer, create_app

app = create_app()
multi_agent_env_server = MultiAgentEnvServer()


@app.post("/add_agent")
async def add_agent(yaml_string: str):
    try:
        is_successed, error_message = multi_agent_env_server.add_agent(yaml_string)
        if is_successed:
            return {"is_successed": is_successed, "error_message": error_message}
        else:
            return {"is_successed": is_successed, "error_message": error_message}
    except Exception as e:
        return {"is_successed": False, "error_message": str(e)}


@app.post("/post_message")
async def post_message(target_agent_name: str, content: str):
    try:
        is_successed, error_message = multi_agent_env_server.post_message(target_agent_name, content)
        if is_successed:
            return {"is_successed": is_successed, "error_message": error_message}
        else:
            return {"is_successed": is_successed, "error_message": error_message}
    except Exception as e:
        return {"is_successed": False, "error_message": str(e)}


# count = 1
# message_cache = [
#     ("bob",
#         Message(
#             send_from = "bob",
#             env_handle_type = EnvironmentHandleType.THOUGHT,
#             content = "这是Bob的第一条测试消息"
#         )
#     ),
#     ("alice",
#     Message(
#         send_from = "alice",
#         env_handle_type = EnvironmentHandleType.THOUGHT,
#         content = "这是Alice的第一条测试消息"
#     ),
#     ),
#     ("bob",
#     Message(
#         send_from = "bob",
#         env_handle_type = EnvironmentHandleType.THOUGHT,
#         content = "这是Bob的第二条测试消息"
#     ),


#     ),
#     ("alice",
#     Message(
#         send_from = "alice",
#         env_handle_type = EnvironmentHandleType.THOUGHT,
#         content = "这是alice的第二条测试消息"
#     ),
#     ),
#     # G:\WiseAgent_V3\WiseAgent\workspace\1.xlsx
#     ("alice",
#     FileUploadMessage(
#         send_from = "alice",
#         file_name=r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\index.html",
#         file_content=read_rb(r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\index.html")
#     ),
#     ),
#     ("bob",
#     FileUploadMessage(
#         send_from = "bob",
#         file_name=r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\style.css",
#         file_content=read_rb(r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\style.css")
#     ),
#     ),
#     ("alice",
#     FileUploadMessage(
#         send_from = "alice",
#         file_name=r"G:\WiseAgent_V3\WiseAgent\workspace\1.xlsx",
#         file_content=read_rb(r"G:\WiseAgent_V3\WiseAgent\workspace\1.xlsx")
#     ),
#     ),
#     ("alice",
#     FileUploadMessage(
#         send_from = "alice",
#         file_name =r"G:\WiseAgent_V3\WiseAgent\workspace\arxiv.json",
#         file_content=read_rb(r"G:\WiseAgent_V3\WiseAgent\workspace\arxiv.json")
#     ),
#     ),
#     ("alice",
#     FileUploadMessage(
#         send_from = "bob",
#         file_name=r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\script.js",
#         file_content=read_rb(r"G:\WiseAgent_V3\WiseAgent\workspace\resume_website\script.js")
#     )
#     ),
# ]
# multi_agent_env_server.message_cache = message_cache
@app.get("/get_message")
async def get_message(position: int):
    try:
        message_list, next_position_tag, new_message = multi_agent_env_server.get_message(position)
        if message:
            message = message.to_json()
        else:
            message = "None"
        return {
            "message_list": message_list,
            "next_position_tag": next_position_tag,
            "new_message": new_message,
        }
    except Exception as e:
        print(3)
        return {"message": str(e), "next_position_tag": position, "has_next": False}


@app.post("/get_agent_list")
async def get_agent_list():
    return {"agent_list": multi_agent_env_server.get_agent_list()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
