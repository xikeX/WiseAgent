"""
Author: Huang Weitao
Date: 2024-09-21 12:59:01
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 19:18:52
Description: ActionMethod Annotation. This will include the action name and the action type.
"""

import functools
import inspect
from collections import defaultdict

from wiseagent.core.agent import get_current_agent_data


def get_dict_description(action) -> dict:
    """
    Get the description of the action class.
    Args:
        action (Action): The action class.
    Returns:
        dict: The description of the action class.
    """
    result = {
        "class_name": action.__name__,
        "class_description": action.__doc__ or "",
        "class_methods": defaultdict(dict),
    }
    for name, method in inspect.getmembers(action, predicate=inspect.isfunction):
        if not hasattr(method, "action"):
            continue
        # Method name
        method_info = {"method_description": method.__doc__ or ""}
        result["class_methods"][name] = {}
        # Method parameters and their types (if available)
        for param in inspect.signature(method).parameters.values():
            if param.name == "self":
                continue
            param_info = {"param_name": param.name}
            if param.annotation != inspect.Parameter.empty:
                param_info["param_type"] = param.annotation.__name__
            method_info.setdefault("params", []).append(param_info)
        result["class_methods"][name] = method_info
    if not result["class_methods"]:
        return {}
    return result


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

        # set the action to True. This wil be used to check if the function is an action.
        wrapper.action = True

        return wrapper

    return decorator
