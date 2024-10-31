"""
Author: Huang Weitao
Date: 2024-09-17 15:30:12
LastEditors: Huang Weitao
LastEditTime: 2024-10-05 12:17:28
Description: 
"""
import base64
import json
from datetime import datetime
from enum import Enum
from typing import Any, List

from pydantic import BaseModel

from wiseagent.config import logger
from wiseagent.core.agent_core import get_agent_core

STREAM_END_FLAG = "[STREAM_END_FLAG]"


class EnvironmentHandleType(str, Enum):
    COMUNICATION = "communication"
    CONTROL = "control"
    THOUGHT = "thought"
    COMMAND = "command"
    BASE_ACTION_MESSAGE = "base_action_message"
    FILE_UPLOAD = "file_upload"
    SLEEP = "sleep"
    WAKEUP = "wakeup"


class LLMHandleType(str, Enum):
    USER = "user"
    AI = "assistant"


class Message(BaseModel):
    send_from: str = ""
    send_to: str = ""
    cause_by: str = ""
    content: str = ""
    time_stamp: str = ""
    env_handle_type: EnvironmentHandleType = None
    llm_handle_type: LLMHandleType = None
    appendix: dict = {}
    track: List[str] = []
    is_stream: bool = False
    # if is_stream is True, queue will be assigned a queue object
    stream_queue: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # To reduce the difficulty of identifying the intelligent agent, convert send_to, send_from to lowercase
        if not self.send_from:
            from wiseagent.agent_data.base_agent_data import get_current_agent_data

            agent_data = get_current_agent_data()
            self.send_from = agent_data.name
        if self.time_stamp == "":
            self.time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.send_to and any(char.isupper() for char in self.send_to):
            logger.warning(f"send_to {self.send_to} contains uppercase letters, convert to lowercase")
            self.send_to = self.send_to.lower()
        if self.send_from and any(char.isupper() for char in self.send_from):
            logger.warning(f"send_from {self.send_from} contains uppercase letters, convert to lowercase")
            self.send_from = self.send_from.lower()

    def _to_dict(self, exclude=[]) -> str:
        # 将 stream_queue 转换为可序列化的格式
        if self.stream_queue is not None and not isinstance(
            self.stream_queue, (str, int, float, bool, list, dict, tuple, set)
        ):
            self.stream_queue = ""  # 或者其他适当的转换方式
        return self.model_dump(exclude=exclude)

    def to_json(self, exclude=[]) -> str:
        data = self._to_dict(exclude)
        return json.dumps(data, ensure_ascii=False)

    def add_image(self, image):
        # TODO: if image is a path, read it
        self.appendix["image"] = image

    def add_audio(self, audio):
        # TODO: if audio is a path, read it
        self.appendix["audio"] = audio

    def send_message(self):
        """
        This is a quick way to report the message to the user.
        Make sure the agent core is active.
        """
        agent_core = get_agent_core()
        if agent_core and agent_core.is_running:
            agent_core.report_message(self)
        else:
            logger.warning("Agent core is not active, cannot send message. Please start the agent core first.")


class AIMessage(Message):
    llm_handle_type: str = LLMHandleType.AI


class UserMessage(Message):
    llm_handle_type: str = LLMHandleType.USER


class ThoughtMessage(Message):
    env_handle_type: str = EnvironmentHandleType.THOUGHT


class CommandMessage(Message):
    env_handle_type: str = EnvironmentHandleType.COMMAND


class CommunicationMessage(Message):
    env_handle_type: str = EnvironmentHandleType.COMUNICATION


class BaseActionMessage(Message):
    env_handle_type: str = EnvironmentHandleType.BASE_ACTION_MESSAGE


class ControlMessage(Message):
    env_handle_type: str = EnvironmentHandleType.CONTROL


class FileUploadMessage(Message):
    env_handle_type: str = EnvironmentHandleType.FILE_UPLOAD
    file_name: str = ""
    file_content: Any = b""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.file_name is "" and self.stream_queue is None:
            raise ValueError("file_name must be specified")
        if self.file_content is b"" and self.file_name:
            from wiseagent.common.file_io import read_rb

            self.file_content = read_rb(self.file_name)

    def to_json(self) -> str:
        data = self._to_dict(exclude=["file_content"])
        data["file_content"] = base64.b64encode(self.file_content).decode("utf-8")
        return json.dumps(data, ensure_ascii=False)


class SleepMessage(Message):
    env_handle_type: str = EnvironmentHandleType.SLEEP


class WakeupMessage(Message):
    env_handle_type: str = EnvironmentHandleType.WAKEUP


if __name__ == "__main__":
    m = Message()
    c = {"message": m.to_json()}
    d = json.dumps(c)
    print(d)
