"""
Author: Huang Weitao
Date: 2024-10-05 00:38:39
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 17:37:43
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


def test_stream():
    message_id = "12345678"
    message = Message(message_id=message_id, is_stream=True, stream_queue=queue.Queue())

    def event_stream():
        for i in range(30):
            game_2048_python_code = """
import random
import time
import numpy as np
import matplotlib.pyplot as plt

def get_empty_position(board):
    empty_positions = []
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                empty_positions.append((i, j))
    return empty_positions

def move(board, direction): 
    if direction == 'up':
        for j in range(4):
            for i in range(1, 4):
                if board[i][j] != 0:
"""
        for ch in game_2048_python_code:
            message.stream_queue.put(ch)
            time.sleep(0.001)
        message.stream_queue.put(STREAM_END_FLAG)

    multi_agent_env_server.message_cache.append(message)
    threading.Thread(target=event_stream).start()
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    # test_stream()
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # test_stream()
