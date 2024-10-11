"""
Author: Huang Weitao
Date: 2024-10-10 22:22:37
LastEditors: Huang Weitao
LastEditTime: 2024-10-11 00:34:38
Description: 
"""
import webbrowser

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.annotation import singleton
from wiseagent.common.file_io import read_rb, repair_path, write_file
from wiseagent.core.agent_core import get_agent_core
from wiseagent.protocol.message import AIMessage, FileUploadMessage

WRITE_CODE_PROMPT_TEMPLATE = """
Your are and Engineer, you need to write some code according to the file description.

## File List
{file_list}

## File Description
{file_description}

## Instruction
Implement the each of the code file according to the file_description. Ensure the code is compete, correct and bug free. Do Not leave any TODOs or comments in the code.

## Output Format
<file_name>
the content of the file name 1
</file_name>
<code>
the code of the file name 1
</code>

<file_name>
the content of the file name 2
</file_name>
<code>
...

Ouput:
"""


@singleton
class WriteCodeAction(BaseAction):
    """This is ActionCass to do wechat action, all the action will be play in Wechat Application"""

    action_name: str = "WriteCodeAction"
    action_description: str = " this class is to do wechat action."

    def init_agent(self, agent_data: AgentData):
        """This Action Does not need to add structure"""

    @action()
    def wirte_code(self, file_list: list[str], file_description: str):
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
        agent_data = get_current_agent_data()
        memory = agent_data.get_last_memory()
        while file_list:
            current_file_list = file_list[:5]
            write_code_prompt = WRITE_CODE_PROMPT_TEMPLATE.format(
                file_list="\n".join(current_file_list), file_description=file_description
            )
            respond = self.llm_ask(write_code_prompt, memory=memory, system_prompt=[])
            current_file_list, code = self.parse_write_code_respond(respond)
            memory.append(AIMessage(coontent=respond))
            output += "\n\n".join(
                [f"{file_name} complete.\ncontent:\n{code}" for file_name, code in zip(current_file_list, code)]
            )
            file_list = file_list[5:]
        return output + "All files are complete."

    def parse_write_code_respond(self, rsp):
        def get_tag_content(tag_name, rsp):
            start_tag = f"<{tag_name}>"
            end_tag = f"</{tag_name}>"
            start_index = rsp.find(start_tag)
            end_index = rsp.find(end_tag)
            if start_index == -1 or end_index == -1:
                return None, rsp
            remaind_rsp = rsp[end_index + len(end_tag) :]
            return rsp[start_index + len(start_tag) : end_index].strip(), remaind_rsp

        file_list = []
        code_list = []
        agent_core = get_agent_core()
        while rsp:
            file_name, rsp = get_tag_content("file_name", rsp)
            code, rsp = get_tag_content("code", rsp)
            if not (file_name and code):
                break
            write_file(file_name, code)
            agent_core.monitor.add_message(FileUploadMessage(file_name=file_name, file_content=read_rb(file_name)))
            file_list.append(file_name)
            code_list.append(code)
        return file_list, code_list

    @action()
    def open_html(self, html_file_path):
        """Open the html file in the browser.
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
