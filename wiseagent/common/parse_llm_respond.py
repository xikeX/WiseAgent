"""
Author: Huang Weitao
Date: 2024-11-03 15:40:54
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 12:05:17
Description: 
"""
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


def parse_code_data(respond):
    """get the code data from the respond"""
    try:
        pattern = re.compile(r"```(.*?)\n(.*?)\n```", re.DOTALL)
        match = pattern.search(respond)
        if not match:
            raise ValueError("No code data found in the respond, please check does it has ```\n...\n```")
        code_data = match.group(2)
        return code_data, None
    except Exception as e:
        return None, str(e)


def get_tag_content(xml_data, tag_name):
    """get the content of the tag
    If the tag contain property,get the property value
    """
    res = {}
    # <args name="message" type = str >Hello, Alice!</args>
    # res = {"value":"innertext","name":"tag_name","type":"tag_type"}
    pattern = r"<{}(.*?)>(.*?)</{}>".format(tag_name, tag_name)
    match = re.search(pattern, xml_data, re.DOTALL)
    if match:
        tag_content = match.group(2)
        if tag_content.strip().startswith("<![CDATA["):
            tag_content = tag_content.strip()[9:-3]
        if tag_content.strip() == "None":
            tag_content = None
        tag_property = match.group(1)
        if tag_property != "":
            pattern = r'\s*(\w+)\s*=\s*["\']?([^"\'>]+)["\']?\s*'
            matches = re.findall(pattern, tag_property, re.DOTALL)
            for match in matches:
                key1, value1 = match
                res[key1] = value1.strip()
        res["value"] = tag_content
        return res
    else:
        return None


def parse_command_xml_data(text):
    """get the xml data from the respond"""
    try:
        rsp = []
        pattern = re.compile(r"```xml\n(.*)\n```", re.DOTALL)
        match = pattern.search(text)
        xml_data = text
        if match:
            xml_data = match.group(1)
        # parse xml data
        action_list = re.compile(r"<action_list>(.*?)</action_list>", re.DOTALL).search(xml_data).group(1)
        actions = re.compile(r"<action>(.*?)</action>", re.DOTALL).findall(action_list)
        for action in actions:
            action_name = get_tag_content(action, "action_name")["value"]
            action_method = get_tag_content(action, "action_method")["value"]
            args = re.compile(r"<args(.*?)>(.*?)</args>", re.DOTALL).findall(action)
            args_dict = {}
            for arg in args:
                orginal_tag = "<args{}>{}</args>".format(arg[0], arg[1])
                cur_arg = get_tag_content(orginal_tag, "args")
                if cur_arg["value"] is None:
                    args_dict[cur_arg["name"]] = None
                elif cur_arg["type"] == "list":
                    args_dict[cur_arg["name"]] = json.loads(cur_arg["value"].replace("'", '"'))
                elif cur_arg["type"] == "int":
                    args_dict[cur_arg["name"]] = int(cur_arg["value"])
                elif cur_arg["type"] == "float":
                    args_dict[cur_arg["name"]] = float(cur_arg["value"])
                elif cur_arg["type"] == "bool":
                    args_dict[cur_arg["name"]] = bool(cur_arg["value"])
                else:
                    args_dict[cur_arg["name"]] = cur_arg["value"]
            rsp.append({"action_name": action_name, "action_method": action_method, "args": args_dict})
        return rsp, None
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    xml_data = """
    <action_list>
    <action>
    <action_name>Chat</action_name>
    <action_method>chat</action_method>
    <args name="send_to" type = str >Alice</args>
    <args name="message" type = str >Hello, Alice!</args>
    </action>
    <action>
    <action_name>Chat</action_name>
    <action_method>chat</action_method>
    <args name="send_to" type = str >Bob</args>
    <args name="message" type = list >["Hello, Bob!", "How are you?"]</args>
    </action>
    <action>
    <action_name>Chat</action_name>
    <action_method>chat</action_method>
    <args name="send_to" type = str >Charlie</args>
    <args name="message" type = int >123</args>
    </action>
    <action>
    <action_name>Chat</action_name>
    <action_method>chat</action_method>
    <args name="send_to" type = str >David</args>
    <args name="message" type = list >None</args>
    </action>
    <action>
    <action_name>Chat</action_name>
    <action_method>chat</action_method>
    <args name="send_to" type = str >Eve</args>
    <args name="message" type = str ><![CDATA[Do you know me?]]></args>
    </action_list>
    """
    print(parse_command_xml_data(xml_data))
