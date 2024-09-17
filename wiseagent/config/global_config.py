'''
Author: Huang Weitao
Date: 2024-09-17 16:06:02
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 16:38:16
Description: 
'''

from wiseagent.common.yaml_config import YamlConfig
from wiseagent.config import CONFIG_PATH


class GlobalConfig(YamlConfig):
    perceptron_model_path:str
    base_receiver_model_path:str
    @classmethod
    def default(cls):
        config_file_path = CONFIG_PATH/'global_config.yaml'
        return cls.from_yaml_file(config_file_path)
    
    def update(self,key,value,mode = 'append'):
        if hasattr(self,key):
            if mode == 'append':
                setattr(self,key,getattr(self,key) + value)
            elif mode == 'overwrite':
                setattr(self,key,value)
            elif mode == 'create':
                raise ValueError('key exist. If you want to overwrite it, use mode = overwrite')
        else:
            if mode =='create':
                setattr(self,key,value)
            else:
                raise ValueError('key not exist')
    
GLOBAL_CONFIG = GlobalConfig.default()