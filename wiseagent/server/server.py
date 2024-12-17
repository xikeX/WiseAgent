"""
Author: Huang Weitao
Date: 2024-10-05 00:38:39
LastEditors: Huang Weitao
LastEditTime: 2024-11-20 11:55:51
Description: 
"""

import json
import queue
import threading
import time

import uvicorn
from fastapi.responses import StreamingResponse

from wiseagent.common.protocol_message import STREAM_END_FLAG, Message
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


# multi_agent_env_server.message_cache = message_cache
@app.get("/get_message")
async def get_message(position: int):
    # try:
    message_list, next_position_tag = multi_agent_env_server.get_message(position)
    if message_list:
        message_list = json.dumps([m._to_dict() for m in message_list])
    else:
        message_list = []
    return {
        "message_list": message_list,
        "next_position_tag": next_position_tag,
    }


@app.get("/get_stream_message")
async def get_stream_message(message_id: str):
    return StreamingResponse(multi_agent_env_server.get_stream_message(message_id), media_type="text/event-stream")


@app.post("/get_agent_list")
async def get_agent_list():
    return {"agent_list": multi_agent_env_server.get_agent_list()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    # test_stream()
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # test_stream()
