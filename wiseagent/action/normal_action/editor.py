"""
Author: Huang Weitao
Date: 2024-10-23 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-10-23 14:24:14
Description:  
"""
import pandas as pd

from wiseagent.action.action_annotation import action
from wiseagent.action.base_action import BaseAction


class EditorAction(BaseAction):
    action_description: str = "EditorAction is a tool for editing files"

    @action()
    def read_excel_or_csv(self, file_path, limit=5):
        """Read excel file and switch to list(dict)
        Args:
            file_path (str): The path of excel file
            limit (int): The limit of rows
        """
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        list_of_dicts = df.to_dict(orient="records")
        list_of_dicts = list_of_dicts[:limit]
        return f"[Observe] Read excel file successfully, The first {limit} rows are:\n{list_of_dicts}\n[End Observe]"

    @action()
    def read_code_or_text(self, file_path):
        """Read code file and switch to list(dict)
        Args:
            file_path (str): The path of code file
            limit (int): The limit of rows
        """
        with open(file_path, "r") as f:
            lines = f.read()
        return f"[Observe] Read code/text file successfully:\n{lines}\n[End Observe]"


def get_action():
    return EditorAction()
