"""
Author: Huang Weitao
Date: 2024-09-19 23:55:33
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 23:38:06
Description: 
"""
import inspect
import json
from collections import defaultdict
from enum import Enum
from typing import Dict

import xmltodict


class DescriptionType(Enum):
    DICT_TYPE = 1
    JSON_TYPE = 2
    XML_TYPE = 3


def _get_action_class_desciprtion(action) -> Dict:
    res = {}
    # class name
    res["class_name"] = action.__class__.__name__
    # class description
    res["class_description"] = action.__doc__
    # class method that have annotated with @action
    res["class_method"] = defaultdict()
    for name, method in inspect.getmembers(action, predicate=inspect.isfunction):
        if hasattr(method, "action"):
            # method name
            res["class_method"][name] = {}
            # mothod parameters name and type(if has)
            for param in inspect.signature(method).parameters.values():
                if param.name != "self":
                    res["class_method"][name]["param"] = {"param_name": param.name}
                    if param.annotation != inspect.Parameter.empty:
                        res["class_method"][name]["param"]["param_type"] = param.annotation.__name__
            # method description
            res["class_method"][name]["method_description"] = method.__doc__
            # return type
            # res['class_method'][name]['return_type'] = method.__annotations__['return'].__name__
    if not res["class_method"]:
        return {}
    return res


def get_action_class_desciprtion(action, description_type=DescriptionType.DICT_TYPE):
    action_class_desciprtion = _get_action_class_desciprtion(action)
    if description_type == DescriptionType.DICT_TYPE:
        return action_class_desciprtion
    elif description_type == DescriptionType.JSON_TYPE:
        return json.dumps(action_class_desciprtion, indent=4)
    elif description_type == DescriptionType.XML_TYPE:
        xml_string = xmltodict.unparse(action_class_desciprtion, pretty=True)
    raise Exception("description_type not supported")


def get_dict_description(action):
    return get_action_class_desciprtion(action)
