"""
Author: Huang Weitao
Date: 2024-10-23 14:24:14
LastEditors: Huang Weitao
LastEditTime: 2024-10-24 10:49:20
Description:  
"""
from functools import partial

import pandas as pd

from wiseagent.action.action_annotation import action
from wiseagent.action.base import BaseAction
from wiseagent.common.file_io import repair_path


class EditorAction(BaseAction):
    action_name: str = "EditorAction"
    action_description: str = "EditorAction is a tool for editing files"
    read_file_map: dict = {}

    def __ini__(self):
        super().__init__()
        self.read_file_map = {
            "xlsx": partial(self.read_excel, read_type="excel"),
            "csv": partial(self.read_excel, read_type="csv"),
            "other": self.read_text,
        }

    @action()
    def read(self, file_name, limit=None):
        """read file
        Args:
            file_name (str): The name of file
            limit (int): The limit of rows. If limit is None, read all rows. When read excel file, limit set to 5, when read code file, limit set to None

        Example:
            >>> read("test.xlsx",limit=5)
            >>> read("app.py")
        """
        suffix = file_name.split(".")[-1]
        read_function = self.read_file_map["other"]
        if suffix in self.read_file_map:
            read_function = self.read_file_map[suffix]
        return read_function(file_name, limit)

    def read_pd(self, file_name, limit=5, file_type="excel"):
        """Read excel file and switch to list(dict)
        Args:
            file_name (str): The path of excel file
            limit (int): The limit of rows
        """
        file_name = repair_path(file_name)
        if file_type == "excel":
            df = pd.read_excel(file_name)
        elif file_type == "csv":
            df = pd.read_csv(file_name)
        list_of_dicts = df.to_dict(orient="records")
        list_of_dicts = list_of_dicts[:limit]
        return f"[Observe] Read excel file successfully, The first {limit} rows are:\n{list_of_dicts}\n[End Observe]"

    def read_text(self, file_name):
        """Read code file and switch to list(dict)
        Args:
            file_name (str): The path of code file
            limit (int): The limit of rows
        """
        file_name = repair_path(file_name)
        with open(file_name, "r") as f:
            lines = f.read()
        return f"[Observe] Read code/text file successfully:\n{lines}\n[End Observe]"

    @action()
    def replace_content(self, file_name, orginal_content, new_content):
        """Replace content in file
        Args:
            file_name (str): The name of file
            orginal_content (str): The orginal content
            new_content (str): The new content
        Example:
            >>> orginal_content = "def remove_empty_space(txt):\n    txt = txt.replace(' ', '')\n    return txt"
            >>> new_content = "def remove_empty_space(txt):\n    txt = txt.replace(' ', '')\n    txt = txt.replace('\n', '')\n    return txt"
            >>> replace_content("app.py",orginal_content,new_content)
        """
        file_name = repair_path(file_name)
        with open(file_name, "r") as f:
            lines = f.read()
        if lines.count(orginal_content) == 0:
            return f"[Observe] The orginal content is not in the file\n[End Observe]"
        elif lines.count(orginal_content) > 1:
            return f"[Observe] The orginal content is in the file more than once\nPlease enlarge the original content\n[End Observe]"
        lines = lines.replace(orginal_content, new_content)
        with open(file_name, "w") as f:
            f.write(lines)
        return f"[Observe] Replace content in file successfully\n[End Observe]"

    @action()
    def insert_content(self, file_name, pre_line, new_content, force=False):
        """Add content below the pre_line
        Args:
            file_name (str): The name of file
            pre_line (str): The line before the new content
            new_content (str): The new content
            force (bool): If False, the function will try to fix, if set to True, the function not check the content.
        Example:
            >>> # the pre content is:
            >>> # def remove_empty_space(txt):
            >>> #     txt = txt.replace(' ', '')
            >>> #     return txt
            >>> insert_content("app.py","def remove_empty_space(txt):",    txt = txt.replace('\n', '')")
            >>> # After execute the function, the new content is:
            >>> # def remove_empty_space(txt):
            >>> #     txt = txt.replace(' ', '')
            >>> #     txt = txt.replace('\n', '')
            >>> #     return txt
        """
        file_name = repair_path(file_name)
        with open(file_name, "r") as f:
            lines = f.read()
            lines = lines.split("\n")
        if lines.count(pre_line) == 0:
            return f"[Observe] The pre_line is not in the file\n[End Observe]"
        elif lines.count(pre_line) > 1:
            return f"[Observe] The pre_line is in the file more than once\nPlease use replace_content\n[End Observe]"
        insert_index = lines.index(pre_line) + 1
        if insert_index == len(lines):
            # insert the content at the end of the file
            lines.append(new_content)
        else:
            if force is False:
                # Check the deplication of the new content
                new_content = new_content.split("\n")
                # Check prefix
                if pre_line in new_content:
                    new_content = new_content[1:]
                # Check suffix
                next_line = lines[insert_index]
                if next_line in new_content:
                    depulication_index = len(new_content) - 1 - new_content[::-1].index(next_line)
                    flag, cur_line = True, 1
                    while depulication_index + cur_line < len(new_content) and insert_index + cur_line < len(lines):
                        if new_content[depulication_index + cur_line] != lines[insert_index + cur_line]:
                            flag = False
                            break
                        cur_line += 1
                    if flag:
                        new_content = new_content[:depulication_index]
                new_content = "\n".join(new_content)
            lines.insert(insert_index, new_content)
            with open(file_name, "w") as f:
                f.write("\n".join(lines))
            return f"[Observe] Insert content in file successfully\n[End Observe]"


def get_action():
    return EditorAction()
