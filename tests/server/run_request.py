import json
import time

import requests

if __name__ == "__main__":
    with open(r"tests\server\arxiv_agent.yaml", "r", encoding="utf-8") as f:
        yaml_string = f.read()
    requests.post("http://127.0.0.1:5000/add_agent", params={"yaml_string": yaml_string})
    # @bob 帮我查看3天内llm和agent相关的论文，并保存
    requests.post(
        "http://127.0.0.1:5000/post_message", params={"target_agent_name": "bob", "content": "帮我收集过去2天与llm相关的论文,并保存"}
    )
    current_id = 0
    while True:
        response = requests.get("http://127.0.0.1:5000/get_message", params={"position": current_id})
        if response.status_code == 200:
            data = response.json()
            message = data["message"]
            next_position_tag = data["next_position_tag"]
            agent_name = data["agent_name"]
            new_message = bool(data["new_message"])
            if new_message:
                print("receiver message", message)
                message = json.loads(message)
                for key in message.keys():
                    print(key, message[key])
                current_id = next_position_tag
        time.sleep(1)
