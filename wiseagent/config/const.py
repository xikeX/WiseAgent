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
WORKING_DIR = ROOT_PATH / "workspace"

# May be used in the future
DATA_PATH = ROOT_PATH / "data"
LOG_PATH = ROOT_PATH / "log"
TEMP_PATH = ROOT_PATH / "temp"
