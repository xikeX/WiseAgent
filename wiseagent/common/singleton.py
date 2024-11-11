"""
Author: Huang Weitao
Date: 2024-09-18 08:53:30
LastEditors: Huang Weitao
LastEditTime: 2024-09-18 08:53:42
Description: sigleton decorator
"""


import functools


def singleton(cls):
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
