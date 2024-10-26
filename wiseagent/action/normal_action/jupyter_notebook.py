import uuid
from typing import Any

import nbformat as nbf
from jupyter_client import BlockingKernelClient, KernelManager
from pydantic import ConfigDict

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction, BaseActionData
from wiseagent.agent_data.base_agent_data import AgentData, get_current_agent_data
from wiseagent.common.file_io import read_rb, repair_path
from wiseagent.protocol.message import FileUploadMessage
from wiseagent.tools.notebook_execute_tool import JupyterNotebookTool


class JupyterNotebookActionData(BaseActionData):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    notebook_tool: JupyterNotebookTool = None

    def __init__(self):
        super().__init__()
        self.notebook_tool = JupyterNotebookTool()


class JupyterNotebookAction(BaseAction):
    action_name: str = "JupyterNotebookAction"
    action_description: str = "This action is used to execute jupyter notebook code"

    def init_agent(self, agent_data: AgentData):
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
        agent_data: AgentData = get_current_agent_data()
        temp_save_file_name = agent_data.agent_id + "temp.ipynb"
        temp_save_file_name = repair_path(temp_save_file_name)
        self._save_notebook(temp_save_file_name)
        return (
            "Code block executed \nOutput:\n" + output + "" if not img_list else "\nImage Size:\n" + str(len(img_list))
        )

    def shutdown(self):
        notebook_tool = self.get_notnotebook_toolebook()
        notebook_tool.shutdown()
        return "Notebook Shut Down"

    def _save_notebook(self, filename, upload_file=False):
        filename = repair_path(filename)
        notebook_tool = self.get_notnotebook_toolebook()
        notebook_tool.save_notebook(filename)
        if upload_file:
            FileUploadMessage(file_content=read_rb(filename)).send_message()
        return filename

    @action()
    def save_notebook(self, filename):
        """Save jupyter notebook.
        Args:
            filename (str): filename to save
        """
        filename = self._save_notebook(filename, upload_file=True)
        return f"Notebook Saved. The file is saved as {filename}"

    def close(self):
        self.shutdown()


def get_action():
    return JupyterNotebookAction()
