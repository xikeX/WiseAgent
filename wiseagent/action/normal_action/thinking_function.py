"""
推理辅助行为集之后就是优化这个伪行为类
"""
"""
Author: Huang Weitao
Date: 2024-09-28 21:15:25
LastEditors: Huang Weitao
LastEditTime: 2024-10-03 11:39:17
Description: 
"""
from datetime import datetime
import json
import time
from typing import Any

from wxauto import WeChat

from wiseagent.action.action_decorator import action
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.parse_llm_respond import parse_json_data
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from pydantic import BaseModel


REASONING_ASSIST_ACTION_GENERATE_PROMPT = """
As an intelligent assistant, you analyze experimental failures, distill the root cause into a clear summary, and offer practical solutions. You then create a reasoning-assist action based on the insights, empowering your teammates to think critically and overcome challenges effectively.

Here is the information, experiment, failure reason and suggestion of your teammates:
## Teammate Information
{teammate_info}

## Experiment Information
{experiment_info}

## Here is the reasoning assist action you have generated:
{reasoning_assist_action}

Now, you task is to generate a reasoning assist action according to the failure reason and suggestion, in order to help your teammates thinking deepthly and solve the problem.
You must output in the following format:
```json
[
    {
        "failure_reason": "The failure reason",
        "suggestion": "The suggestion",
        "action_name": "The reasoning assist action name",
        "action_description": "The description of the action, incuding when to use this action, what to do, and what to pay attention to",
        "action_params": [
            "param_name(param_type)": "The description of the param",
            ...
        ]
        "return_format": "A f-format string, to organize the input params to a clear and structured format."
    }
    ...
]
"""
REASONING_ASSIST_ACTION_FORMAT="""
{{

    "action_name": "{action_name}",
    "action_description":"{action_description}",
    "action_params": {params},
    "return_format": "{return_format}"
}}
""".strip()
class ReasoningAssistActionNode(BaseModel):
    name: str
    action_description: str
    params: Any
    return_format:str
    def __init__(self,name, params:Any, action_description:str, return_format:str):
        self.name = name
        self.params = params
        self.action_description = action_description
        self.return_format = return_format
        
class ReasoningAssistActionSet(BaseModel):
    action_nodes: list = []
    def __init__(self, action_nodes:list=[]):
        for item in action_nodes:
            self.action_nodes.append(
                ReasoningAssistActionNode(
                    name=item['name'],
                    params=json.loads(item['params']) if isinstance(item['params'], str) else item['params'],
                    action_description=item['action_description'],
                    return_format=item['return_format']
                )
            )
    def append(self, action_node:ReasoningAssistActionNode):
        self.action_nodes.append(action_node)
    

            
class ReasoningAssistActionData(BaseActionData):
    reasoning_assist_action_map: dict = {}
    def __init__(self, action_tree:dict={},default_key:str=''):
        super().__init__()
        for key in action_tree:
            self.reasoning_assist_action_map[key] = ReasoningAssistActionSet(action_tree[key])
        if len(self.reasoning_assist_action_map) == 0:
            self.reasoning_assist_action_map['root'] = ReasoningAssistActionSet(
                action_nodes=[
                    {"name":"think","params":["thinking_context"]}
                ]
            )
        self.default_key = default_key if default_key else 'root'
        self.current_key = self.default_key

    def call(self,name,**args):
        action_node: ReasoningAssistActionNode
        for action_node in self.reasoning_assist_action_map[self.current_key].action_nodes:
            if action_node.name == name:
                return action_node.return_format.format(**args)
        return f"{name} not found in current Reasoning Assist Action."
    
    def get_class_methods(self,key=None,switch_key=True):
        """
        set and get reasoning assist action
        Args:
            key: the key of reasoning assist action, if key is None, use default key.
            switch_key: if switch_key is True, switch to the key of reasoning assist action.
        """
        if key ==None:
            key = self.default_key
        class_methods = {}
        node:ReasoningAssistActionNode
        for node in self.reasoning_assist_action_map[key].action_nodes:
            class_methods[node.name] = {"name":node.name,"description":node.action_description,"param":node.params}
        if switch_key:
            self.current_key = key
        self.current_key = key
        return class_methods
    
    def get(self, key:str=None):
        if key is None:
            return self.reasoning_assist_action_map[self.current_key]
        return self.reasoning_assist_action_map.get(key)

    def set(self, key:str, value:ReasoningAssistActionSet):
        self.reasoning_assist_action_map[key] = value

class ReasoningAssistAction(BaseAction):
    def __init__(self):
        super().__init__()

    def init_agent(self,agent_data):
        action_config = agent_data.get_action_config(self.action_name)
        action_data = ReasoningAssistActionData(
            action_tree=action_config.get('action_tree',{}),
            default_key=action_config.get('default_key','')
        )
        self.set_action_data(action_data)
        self.action_description['class_methods'] = action_data.get_class_methods()

    def add_action_set(self,key,action_set:ReasoningAssistActionSet, switch=False, agent_data=None):
        if agent_data is None:
            agent_data = get_current_agent_data()
        action_data:ReasoningAssistActionData = agent_data.get_action_data(self.action_name)
        action_data.set(key,action_set)
        if switch:
            self.switch_action_set(key)

    def switch_action_set(self,key,agent_data=None):
        self.action_description['class_methos'] = {}
        if agent_data is None:
            agent_data = get_current_agent_data()
        action_data:ReasoningAssistActionData = agent_data.get_action_data(self.action_name)
        self.action_description['class_methods'] = action_data.get_class_methods(key)

    def __getattr__(self, name):
        """when calling mcp methods, but the method is not defined in this class, then call the method in mcp_data_class"""
        agent_data = get_current_agent_data()
        if name not in self.action_description['class_methods']:
            return f"Method {name} not found in MCPAction"
        def method(**kwargs):
            return agent_data.get_action_data(self.action_name).call(name, kwargs)
        return method

    def update(self, agent_data:"Agent",task_name = 'None',switch = False):
        """
        TODO: update action set
        """
        action_data:ReasoningAssistActionData = agent_data.get_action_data(self.action_name)
        experiment_list = agent_data.get_experiment(task_name)
        # TODO: clip the experiment list
        experiment_info_str = '\n'.join([f"Experiment {index}:\n{experiment}" for index,experiment in enumerate(experiment_list.values(),start=1)])
        teammate_info_str = agent_data.get_environment_description()
        # from current keyword to generate reasoning assist action

        reasoning_assist_action_set = action_data.get()
        reasoning_assist_action_str = "[\n"
        action_node:ReasoningAssistActionNode
        for action_node in reasoning_assist_action_set:
            action_node_str = REASONING_ASSIST_ACTION_FORMAT.format(
                action_name=action_node.name,
                action_description=action_node.action_description,
                action_params = action_node.params,
                return_format = action_node.return_format
            )
            reasoning_assist_action_str += action_node_str + ",\n"
        reasoning_assist_action_str += "]"
        prompt = REASONING_ASSIST_ACTION_GENERATE_PROMPT.format(
            teammate_info=teammate_info_str,
            experiment_info=experiment_info_str,
            reasoning_assist_action=reasoning_assist_action_str,
        )
        experiment = agent_data.get_experiment(experiment)
        responds = self.llm_ask(
            prompt=prompt
        )
        action_set = parse_json_data(responds)
        # [
        #     {
        #         "action_name": "The reasoning assist action name",
        #         "action_description": "The description of the action, incuding when to use this action, what to do, and what to pay attention to",
        #         "action_params": [
        #             "param_name(param_type)": "The description of the param",
        #             ...
        #         ]
        #     }
        #     ...
        # ]
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        new_key = task_name+ timestamp
        reasoning_assist_action_set = ReasoningAssistActionSet()
        for action in action_set:
            reasoning_assist_action =ReasoningAssistActionNode(
                name=action['action_name'],
                action_description=action['action_description'],
                params=action['action_params'],
                return_format=action['return_format'],
            )
            reasoning_assist_action_set.append(reasoning_assist_action)
        action_data.set(new_key, reasoning_assist_action_set)
        if switch:
            self.action_description['class_methods'] = action_data.get_class_methods(new_key,switch_key=True)
        
class MCTSReasoningAsistAction(ReasoningAssistAction):

    def update(self, action_set, task_name, switch=False):
        action_data = self.action_description['action_data']
        
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        
        # add the expe

        new_key = task_name+ timestamp
        reasoning_assist_action_set = ReasoningAssistActionSet()
        
        for action in action_set:
            reasoning_assist_action =ReasoningAssistActionNode()
        