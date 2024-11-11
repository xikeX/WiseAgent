"""
Author: Huang Weitao
Date: 2024-09-17 14:24:54
LastEditors: Huang Weitao
LastEditTime: 2024-11-09 10:59:32
Description: 
"""
import os
from pathlib import Path

# Get the absolute path of the current file
current_file_abs_path = os.path.abspath(__file__)

# Agent System Path
ROOT_PATH = Path(current_file_abs_path).parent.parent.parent.resolve()
WISEAGENT_PACKAGE_PATH = ROOT_PATH / "wiseagent"
ENV_CONFIG_PATH = ROOT_PATH / "config" / "env.yaml"
CONFIG_PATH = ROOT_PATH / "config"
WORKING_DIR = ROOT_PATH / "workspace"

# May be used in the future
DATA_PATH = ROOT_PATH / "data"
LOG_PATH = ROOT_PATH / "log"
TEMP_PATH = ROOT_PATH / "temp"

STREAM_END_FLAG = "[STREAM_END_FLAG]"
