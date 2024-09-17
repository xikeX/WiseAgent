'''
Author: Huang Weitao
Date: 2024-09-17 14:24:54
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 17:38:37
Description: 
'''
import os
from pathlib import Path

# 获取当前文件的绝对路径
current_file_abs_path = os.path.abspath(__file__)

ROOT_PATH = Path(current_file_abs_path).parent.parent.parent
CONFIG_PATH = ROOT_PATH / 'config'
