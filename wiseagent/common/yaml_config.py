"""
Author: Huang Weitao
Date: 2024-09-17 16:08:42
LastEditors: Huang Weitao
LastEditTime: 2024-10-06 16:28:16
Description: 
"""
from pathlib import Path
from typing import Dict, Union

import yaml


class YamlConfig:
    """
    A class to handle YAML configuration files. It provides methods to read from and write to YAML files,
    as well as to create an instance from a YAML string.
    """

    _default_path: str = ""

    @classmethod
    def read_yaml(cls, file_path: Union[Path, str], encoding: str = "utf-8") -> Dict:
        """Read yaml file and return a dict"""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding=encoding) as file:
            return yaml.safe_load(file)

    @classmethod
    def from_yaml_file(cls, file_path: Union[Path, str]) -> "YamlConfig":
        parameter = cls.read_yaml(file_path)
        return cls(**parameter)

    @classmethod
    def from_yaml_string(cls, string: str) -> "YamlConfig":
        parameter = yaml.safe_load(string)
        return cls(**parameter)

    @classmethod
    def to_yaml_file(self, file_path: Path, encoding: str = "utf-8") -> None:
        # TODO: memory can not be save and load throught yaml
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with open(file_path, "w", encoding=encoding) as file:
            yaml.safe_dump(self.model_dump(), file)
