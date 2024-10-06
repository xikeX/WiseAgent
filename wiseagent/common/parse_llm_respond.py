import json
import re


def parse_json_data(respond):
    """get the json data from the respond"""
    try:
        pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
        match = pattern.search(respond)
        if not match:
            raise ValueError("No json data found in the respond, please check does it has ```json\n...\n```")
        json_data = match.group(1)
        try:
            rsp = json.loads(json_data)
        except Exception as e:
            raise ValueError("Invalid json data, please check the json format")
        return rsp, None
    except Exception as e:
        return None, str(e)
