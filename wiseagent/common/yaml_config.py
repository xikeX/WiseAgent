from pathlib import Path
from typing import Dict

import yaml


class YamlConfig:
    _default_path = ""
    @classmethod
    def read_yaml(cls, file_path: Path, encoding: str = "utf-8") -> Dict:
        """Read yaml file and return a dict"""
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding=encoding) as file:
            return yaml.safe_load(file)

    @classmethod
    def from_yaml_file(cls, file_path: Path) -> "YamlConfig":
        return cls(**cls.read_yaml(file_path))

    @classmethod
    def to_yaml_file(self, file_path: Path, encoding: str = "utf-8") -> None:
        # TODO: memory can not be save and load throught yaml
        with open(file_path, "w", encoding=encoding) as file:
            yaml.safe_dump(self.model_dump(), file)