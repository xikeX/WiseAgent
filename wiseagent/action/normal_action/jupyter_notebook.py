"""
Author: Huang Weitao
Date: 2024-11-03 15:40:54
LastEditors: Huang Weitao
LastEditTime: 2024-11-08 17:03:34
Description: 
"""


from pydantic import ConfigDict

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.protocol_message import FileUploadMessage
from wiseagent.common.utils import read_rb, repair_path
from wiseagent.tools.notebook_execute_tool import JupyterNotebookTool


class JupyterNotebookActionData(BaseActionData):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    notebook_tool: JupyterNotebookTool = None

    def __init__(self):
        super().__init__()
        self.notebook_tool = JupyterNotebookTool()


class JupyterNotebookAction(BaseAction):
    action_description: str = "This action is used to execute jupyter notebook code"

    def init_agent(self, agent_data: "AgentData"):
        agent_data.set_action_data(self.action_name, JupyterNotebookActionData())

    def get_notnotebook_toolebook(self) -> JupyterNotebookTool:
        return self.get_current_action_data().notebook_tool

    @action()
    def execute_code(self, code_block):
        """Execute code in jupyter notebook
        Args:
            code_block (str): code to execute
        """
        notebook_tool = self.get_notnotebook_toolebook()
        output, img_list = notebook_tool.execute_code(code_block)
        # agent_data: AgentData = get_current_agent_data()
        # temp_save_file_name = agent_data.agent_id + "temp.ipynb"
        # temp_save_file_name = repair_path(temp_save_file_name)
        # self._save_notebook(temp_save_file_name)
        return (
            "Code block executed \nOutput:\n" + output + "" if not img_list else "\nImage Size:\n" + str(len(img_list))
        )

    def shutdown(self):
        notebook_tool = self.get_notnotebook_toolebook()
        notebook_tool.shutdown()
        return "Notebook Shut Down"

    def _save_notebook(self, file_name, upload_file=False):
        file_name = repair_path(file_name)
        notebook_tool = self.get_notnotebook_toolebook()
        notebook_tool.save_notebook(file_name)
        if upload_file:
            FileUploadMessage(file_name=str(file_name), file_content=read_rb(file_name)).send_message()
        return file_name

    @action()
    def save_notebook(self, file_name):
        """Save jupyter notebook.
        Args:
            filename (str): filename to save
        """
        file_name = self._save_notebook(file_name, upload_file=True)
        return f"Notebook Saved. The file is saved as {file_name}"

    def close(self):
        self.shutdown()


def get_action():
    return JupyterNotebookAction()
