"""
Author: Huang Weitao
Date: 2024-09-17 15:30:12
LastEditors: Huang Weitao
LastEditTime: 2024-10-05 12:17:28
Description: 
"""
import base64
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from wiseagent.common.logs import logger
from wiseagent.core.agent_core import get_agent_core

STREAM_END_FLAG = "[STREAM_END_FLAG]"


class EnvironmentHandleType():
    COMMUNICATION = "communication"
    CONTROL = "control"
    THOUGHT = "thought"
    COMMAND = "command"
    BASE_ACTION_MESSAGE = "base_action_message"
    FILE_UPLOAD = "file_upload"
    SLEEP = "sleep"
    WAKEUP = "wakeup"
    CREATE_TASK = "create_task"
    FINISH_TASK = "finish_task"


class LLMHandleType():
    USER = "user"
    AI = "assistant"
    LLM = "assistant"


class Message(BaseModel):
    message_id: str = ""
    send_from: str = ""
    send_to: str = ""
    cause_by: str = ""
    content: str = ""
    time_stamp: str = ""
    env_handle_type: EnvironmentHandleType = None
    llm_handle_type: LLMHandleType = None
    appendix: dict = {}
    is_stream: bool = False
    # if is_stream is True, queue will be assigned a queue object
    stream_queue: Any = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.message_id == "":
            self.message_id = uuid.uuid4().hex
        if not self.send_from or not self.send_to:
            from wiseagent.core.agent import get_current_agent_data

            agent_data = get_current_agent_data()
            if agent_data and not self.send_from:
                self.send_from = agent_data.name
            if agent_data and not self.send_to:
                self.send_to = agent_data.name
        if self.time_stamp == "":
            self.time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.send_to and any(char.isupper() for char in self.send_to):
            self.send_to = self.send_to.lower()
        if self.send_from and any(char.isupper() for char in self.send_from):
            self.send_from = self.send_from.lower()

    def _to_dict(self, exclude=[]) -> str:
        data = self.model_dump(exclude=exclude.append("stream_queue"))
        data["MessageClass"] = self.__class__.__name__
        data["stream_queue"] = ""
        return data

    def to_json(self, exclude=[]) -> str:
        data = self._to_dict(exclude)
        return json.dumps(data, ensure_ascii=False)

    def add_image(self, image):
        # TODO: if image is a path, read it
        self.appendix["image"] = image

    def add_audio(self, audio):
        # TODO: if audio is a path, read it
        self.appendix["audio"] = audio

    def send_message(self) -> "Message":
        """
        This is a quick way to report the message to the user.
        Make sure the agent core is active.
        Returns:
            self
        """
        if self.env_handle_type == None:
            raise ValueError("env_handle_type is not set")
        agent_core = get_agent_core()
        if agent_core and agent_core.is_running:
            agent_core.report_message(self)
            return self
        else:
            logger.warning("Agent core is not active, cannot send message. Please start the agent core first.")
            return self


class AIMessage(Message):
    llm_handle_type: str = LLMHandleType.AI


class UserMessage(Message):
    llm_handle_type: str = LLMHandleType.USER


class ThoughtMessage(Message):
    env_handle_type: str = EnvironmentHandleType.THOUGHT


class CommandMessage(Message):
    env_handle_type: str = EnvironmentHandleType.COMMAND


class CommunicationMessage(Message):
    env_handle_type: str = EnvironmentHandleType.COMMUNICATION


class BaseActionMessage(Message):
    env_handle_type: str = EnvironmentHandleType.BASE_ACTION_MESSAGE


class ControlMessage(Message):
    env_handle_type: str = EnvironmentHandleType.CONTROL


class FileUploadMessage(Message):
    """
    NOTE: This message will not save to the database.
    """

    env_handle_type: str = EnvironmentHandleType.FILE_UPLOAD
    file_name: str = ""
    file_content: Any = b""

    @field_validator("file_name", mode="before")
    def convert_to_path(cls, v):
        if isinstance(v, Path):
            return str(v)
        return v

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.file_name == "" and self.stream_queue is None:
            raise ValueError("file_name must be specified")
        if self.file_content == b"" and self.file_name and not self.is_stream:
            from wiseagent.common.utils import read_rb

            self.file_content = read_rb(self.file_name)

    def _to_dict(self, exclude=["file_content"]):
        data = super()._to_dict(exclude=exclude)
        data["file_content"] = base64.b64encode(self.file_content).decode("utf-8")
        return data


class SleepMessage(Message):
    env_handle_type: str = EnvironmentHandleType.SLEEP


class WakeupMessage(Message):
    env_handle_type: str = EnvironmentHandleType.WAKEUP


class CreateTaskMessage(Message):
    env_handle_type: str = EnvironmentHandleType.CREATE_TASK


class FinishTaskMessage(Message):
    env_handle_type: str = EnvironmentHandleType.FINISH_TASK


MESSAGE_MAP = {
    "AIMessage": AIMessage,
    "UserMessage": UserMessage,
    "ThoughtMessage": ThoughtMessage,
    "CommandMessage": CommandMessage,
    "CommunicationMessage": CommunicationMessage,
    "BaseActionMessage": BaseActionMessage,
    "ControlMessage": ControlMessage,
    "FileUploadMessage": FileUploadMessage,
    "SleepMessage": SleepMessage,
    "WakeupMessage": WakeupMessage,
    "CreateTaskMessage": CreateTaskMessage,
    "FinishTaskMessage": FinishTaskMessage,
}


def get_message_from_dict(data: dict):
    return MESSAGE_MAP[data["message_type"]](**data)


# TODO: add more message types

if __name__ == "__main__":
    m = Message()
    c = {"message": m.to_json()}
    d = json.dumps(c)
    print(d)
