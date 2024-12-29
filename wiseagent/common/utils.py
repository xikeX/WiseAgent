"""
Author: Huang Weitao
Date: 2024-11-04 15:38:50
LastEditors: Huang Weitao
LastEditTime: 2024-11-09 11:05:41
Description: 
"""


import json
import re
from pathlib import Path
from typing import Union

import pandas as pd


def listdir(folder: Path, deepth, filter=None):
    res = []
    if isinstance(folder, str):
        folder = Path(folder)
    for file in folder.iterdir():
        if file.is_dir():
            res.extend(listdir(file, deepth + 1, filter))
        elif filter is None or filter(file):
            res.append((file, deepth))
    return res


def repair_path(path: Union[Path, str]):
    # If the path is not absolute, make it absolute based on the working directory of the current agent
    illegal_chars = r'[*?"<>|\x00-\x1f]'
    path = re.sub(illegal_chars, "", str(path))
    if not Path(path).is_absolute():
        from wiseagent.core.agent import get_current_agent_data

        agent_data = get_current_agent_data()
        working_dir = agent_data.get_working_dir() if agent_data else "workspace"
        path = Path(working_dir) / path
    return Path(path).resolve().absolute()

def read_file(path: Union[Path, str], encoding="utf-8"):
    path = Path(path)
    path = repair_path(path)
    with open(path, "r", encoding=encoding) as f:
        return f.read()
    

def read_file(path: Union[Path, str], encoding="utf-8"):
    path = Path(path)
    path = repair_path(path)
    try:
        content = ""
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        if path.suffix == ".json":
            content = json.loads(content)
        return content
    except Exception as e:
        raise e


def write_file(path: Union[Path, str], content, encoding="utf-8"):
    path = Path(path)
    path = repair_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding=encoding) as f:
            if path.suffix == ".json":
                json.dump(content, f, ensure_ascii=False, indent=4)
            else:
                f.write(content)
    except Exception as e:
        raise e


def read_rb(path: Union[Path, str]):
    # remove unexpected characters in file:
    path = Path(path)
    path = repair_path(path)
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception as e:
        raise e


def write_excel(path: Union[Path, str], data):
    """Save data to excel file. The data should be a list of dictionaries, and the path must end with .xlsx."""
    # If the path is not absolute, make it absolute based on the working directory of the current agent
    path = Path(path)
    path = repair_path(path)
    if path.suffix != ".xlsx":
        path = path.with_suffix(".xlsx")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert the data to a pandas DataFrame and save it to the file
    try:
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
    except Exception as e:
        raise e
