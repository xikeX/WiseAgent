"""
Author: Huang Weitao
Date: 2024-09-19 23:55:33
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 13:05:20
Description: 
"""
import inspect
import json
from collections import defaultdict
from enum import Enum

import xmltodict


class DescriptionType(Enum):
    DICT_TYPE = 1
    JSON_TYPE = 2
    XML_TYPE = 3


def get_dict_description(action) -> dict:
    """
    Get the description of the action class.
    Args:
        action (Action): The action class.
    Returns:
        dict: The description of the action class.
    """
    result = {
        "class_name": action.__class__.__name__,
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


def get_action_class_desciprtion(action, description_type=DescriptionType.DICT_TYPE):
    """
    Get the description of the action class.
    Args:
        action (Action): The action class.
        description_type (DescriptionType): The type of description to return.
    """
    action_class_desciprtion = get_dict_description(action)
    if description_type == DescriptionType.DICT_TYPE:
        return action_class_desciprtion
    elif description_type == DescriptionType.JSON_TYPE:
        return json.dumps(action_class_desciprtion, indent=4)
    elif description_type == DescriptionType.XML_TYPE:
        return xmltodict.unparse(action_class_desciprtion, pretty=True)
    raise Exception("description_type not supported")
