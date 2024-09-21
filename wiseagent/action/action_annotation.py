"""
Author: Huang Weitao
Date: 2024-09-21 12:59:01
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 19:18:52
Description: ActionMethod Annotation. This will include the action name and the action type.
NOTE:
    The action annotation must be:
    @action()
    If developer want to use in this way:
    @action
    It will cause the error.
"""

import functools


def action(use_knowledge=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 在这里可以添加一些预处理逻辑
            result = func(*args, **kwargs)
            # 在这里可以添加一些后处理逻辑
            return result

        # 将自定义属性添加到 wrapper 上
        wrapper.action = True

        # 将自定义属性复制到原始函数上
        setattr(func, "use_knowledge", use_knowledge)

        return wrapper

    return decorator
