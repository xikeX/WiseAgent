"""
Author: Huang Weitao
Date: 2024-10-27 12:18:18
LastEditors: Huang Weitao
LastEditTime: 2024-11-09 11:04:58
Description: 
"""
import sys
from datetime import datetime

from loguru import logger as _logger

from wiseagent.common.const import LOG_PATH


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = f"{name}_{formatted_date}" if name else formatted_date

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(LOG_PATH / f"{log_name}.txt", level=logfile_level)
    return _logger


logger = define_log_level()
