"""
Author: Huang Weitao
Date: 2024-10-05 00:38:39
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:14:11
Description: 
"""

import uvicorn

from wiseagent.protocol.message import FileUploadMessage
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


@app.get("/get_message")
async def get_message(position: int):
    # try:
    agent_name, message, next_position_tag, new_message = None, None, 0, False
    if position == 0:
        message = FileUploadMessage(send_from="bob", file_name="1.md", file_content=open("1.md", "rb").read())
        agent_name, message, next_position_tag, new_message = "Bob", message, 1, True
    # agent_name,message,next_position_tag,has_next = multi_agent_env_server.get_message(position)
    if message:
        message = message.to_json()
    else:
        message = "None"
    return {
        "agent_name": agent_name,
        "message": message,
        "next_position_tag": next_position_tag,
        "new_message": new_message,
    }


# except Exception as e:
#     print(3)
#     return {"message":str(e),"next_position_tag":position,"has_next":False}


@app.post("/get_agent_list")
async def get_agent_list():
    return {"agent_list": ["bob"]}
    # return {"agent_list":multi_agent_env_server.get_agent_list()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
