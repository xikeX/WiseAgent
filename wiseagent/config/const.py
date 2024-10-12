"""
Author: Huang Weitao
Date: 2024-09-19 23:53:17
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 20:46:39
Description: 
"""
"""
Author: Huang Weitao
Date: 2024-09-17 14:24:54
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:18:55
Description: 
"""
import os
from pathlib import Path

# Get the absolute path of the current file
current_file_abs_path = os.path.abspath(__file__)

# Agent System Path
ROOT_PATH = Path(current_file_abs_path).parent.parent
CONFIG_PATH = ROOT_PATH / "config"
WORKING_DIR = ROOT_PATH.parent / "workspace"

# May be used in the future
DATA_PATH = ROOT_PATH.parent / "data"
LOG_PATH = ROOT_PATH.parent / "log"
TEMP_PATH = ROOT_PATH.parent / "temp"
