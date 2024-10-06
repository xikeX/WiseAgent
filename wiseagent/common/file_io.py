"""
Author: Huang Weitao
Date: 2024-10-06 12:10:25
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 12:16:35
Description: 
"""

from pathlib import Path
from typing import Union

import pandas as pd

from wiseagent.agent_data.base_agent_data import get_current_agent_data


def repair_path(path: Union[Path, str]):
    # If the path is not absolute, make it absolute based on the working directory of the current agent
    agent_data = get_current_agent_data()
    working_dir = agent_data.get_working_dir()
    if not Path(path).is_absolute():
        path = Path(working_dir) / path
    return path


def write_file(path: Union[Path, str], content, encoding="utf-8"):
    path = Path(path)
    path = repair_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise e


def write_excel(path: Union[Path, str], data):
    """Save data to excel file. The data should be a list of dictionaries, and the path must end with .xlsx."""

    # If the path is not absolute, make it absolute based on the working directory of the current agent
    path = Path(path)
    path = repair_path(path)
    if path.suffix != ".xlsx":
        raise ValueError("The path must end with .xlsx")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert the data to a pandas DataFrame and save it to the file
    try:
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
    except Exception as e:
        raise e
