"""
Author: Huang Weitao
Date: 2024-10-10 22:22:37
LastEditors: Huang Weitao
LastEditTime: 2024-11-05 10:33:19
Description: 
"""
import itertools
import queue
import re
import webbrowser
from functools import partial
from typing import List

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseAction
from wiseagent.common.protocol_message import (
    STREAM_END_FLAG,
    AIMessage,
    FileUploadMessage,
)
from wiseagent.common.singleton import singleton
from wiseagent.common.utils import repair_path, write_file
from wiseagent.core.agent import Agent, get_current_agent_data

FILE_NAME_START_TAG = "<file_name>"
FILE_NAME_END_TAG = "</file_name>"
CODE_START_TAG = "<code>"
CODE_END_TAG = "</code>"

WRITE_CODE_PROMPT_TEMPLATE = f"""
Your are and Engineer, you need to write some code according to the file description.

## File List
{{file_list}}

## File Description
{{file_description}}

## Instruction
Implement the each of the code file according to the file_description. Ensure the code is compete, correct and bug free. Do Not leave any TODOs or comments in the code.
Do not leave "```" in front of the code block.
## Output Format
{FILE_NAME_START_TAG}
the content of the file name 1
{FILE_NAME_END_TAG}
{CODE_START_TAG}
the code of the file name 1
{CODE_END_TAG}

{FILE_NAME_START_TAG}
the content of the file name 2
{FILE_NAME_END_TAG}
{CODE_START_TAG}
...

Ouput:
"""


@singleton
class WriteCodeAction(BaseAction):
    """This is ActionCass to do wechat action, all the action will be play in Wechat Application"""

    action_description: str = " this class is to do wechat action."

    def init_agent(self, agent_data: Agent):
        """This Action Does not need to add structure"""

    @action()
    def write_code(self, file_list: list[str], file_description: str):
        """Impletement the code file according to the file_description.
        Args:
            file_list (list[str]): the list of the file name
            file_description (str): the description of the file

        Returns:
            list : the list of the complete file path.

        Example:
            >>> self.write_code(
                file_list=[
                    "{project_name}/index.html",
                    "{project_name}/main.js",
                    "{project_name}/styles.css"
                ],
                file_description="This is a simple web page. The index.html file contains the HTML structure, the main.js file contains the JavaScript code, and the styles.css file contains the CSS styles."
            )
        """
        output = ""
        temp_memory = get_current_agent_data().get_latest_memory()
        for current_file_list in [file_list[i : i + 5] for i in range(0, len(file_list), 5)]:
            """Write code for each five files"""
            write_code_prompt = WRITE_CODE_PROMPT_TEMPLATE.format(
                file_list="\n".join(current_file_list), file_description=file_description
            )
            # the will be multi file generate in one respond, so need to report a list of FileUpload Message
            cache = {}
            respond = self.llm_ask(
                write_code_prompt,
                memory=temp_memory,
                handle_stream_function=partial(self.handle_write_code_stream, cache=cache),
            )
            current_file_list, code = self.parse_write_code_respond(respond)
            temp_memory.append(AIMessage(coontent=respond))
            output += "\n\n".join(
                [f"{file_name} complete.\ncontent:\n{code}" for file_name, code in zip(current_file_list, code)]
            )
        return output + "All files are complete."

    def handle_write_code_stream(self, rsp_message: str, cache: dict):
        """
        Prase the stream message and return the file name and file content
        Agrs:
            rsp_message (str): the stream message from LLM, the rsp_message will only add one char per round.
            upload_message (FileUploadMessage): the upload message to upload the file
        """
        if not isinstance(cache, dict):
            raise Exception("cache is not initialized, please use {} to init cache")
        if "file_number" not in cache:
            cache["file_number"] = ""
        if "message_list" not in cache:
            cache["message_list"] = []
        if "message_index" not in cache:
            cache["message_index"] = -1
        if "start_receive_code" not in cache:
            cache["start_receive_code"] = False
        if "start_receive_file_name" not in cache:
            cache["start_receive_file_name"] = False
            cache["file_name"] = ""
        if STREAM_END_FLAG in rsp_message:
            try:
                cache["message_list"][cache["message_index"]].stream_queue.put(STREAM_END_FLAG)
            except Exception as e:
                pass
        special_tag = [FILE_NAME_START_TAG, FILE_NAME_END_TAG, CODE_START_TAG, CODE_END_TAG]
        if any(tag.startswith(rsp_message) for tag in special_tag):
            # Step One, wait for receiver file_name
            if FILE_NAME_END_TAG in rsp_message:
                file_name = repair_path(cache["file_name"].strip())
                cache["message_list"].append(
                    FileUploadMessage(
                        file_name=str(file_name), is_stream=True, stream_queue=queue.Queue()
                    ).send_message()
                )
                cache["message_index"] = cache["message_index"] + 1
                cache["file_name"] = ""
                cache["start_receive_file_name"] = False
                return ""
            # Step Two, start to receive code
            elif FILE_NAME_START_TAG == rsp_message:
                cache["start_receive_file_name"] = True
                return ""
            elif CODE_START_TAG == rsp_message:
                cache["start_receive_code"] = True
                return ""
            # Step Three, stop to receive code
            elif CODE_END_TAG in rsp_message:
                cache["start_receive_code"] = False
                message_index = cache["message_index"]
                cache["message_list"][message_index].stream_queue.put(STREAM_END_FLAG)
                return ""
            return rsp_message
        else:
            # Receive code
            if cache["start_receive_code"]:
                message_index = cache["message_index"]
                cache["message_list"][message_index].stream_queue.put(rsp_message)
            # Receive file name
            if cache["start_receive_file_name"]:
                cache["file_name"] += rsp_message
            return ""

    def parse_write_code_respond(self, rsp):
        """Parse the respond from LLM and return the file name and file content"""
        file_list, code_list = [], []
        pattern = rf"{FILE_NAME_START_TAG}\s*(.*?)\s*{FILE_NAME_END_TAG}\s*{CODE_START_TAG}\s*(.*?)\s*{CODE_END_TAG}"
        write_code_pattern = re.compile(pattern, re.DOTALL)
        match = write_code_pattern.findall(rsp)
        for file_name, code in match:
            write_file(file_name, code)
            file_list.append(file_name)
            code_list.append(code)
        return file_list, code_list

    @action()
    def open_html(self, html_file_path):
        """Open the native html project in the browser.
        Args:
            html_file_path (str): the path of the html file

        Example:
            >>> self.open_html("2048_game/index.html")
        """
        html_file_path = repair_path(html_file_path)
        webbrowser.open(html_file_path)
        return f" {html_file_path} has been opened in the browser."


def get_action():
    return WriteCodeAction()
