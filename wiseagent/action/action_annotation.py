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

from wiseagent.agent_data.base_agent_data import get_current_agent_data


def action(use_knowledge=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if use_knowledge:
                # set the action knowledge
                current_agent_data = get_current_agent_data()
                current_agent_data.set_action_knowledge()
            # call the action function
            result = func(*args, **kwargs)
            if use_knowledge:
                # clean the action knowledge
                current_agent_data.set_action()
            return result

        # 将自定义属性添加到 wrapper 上
        wrapper.action = True

        return wrapper

    return decorator
