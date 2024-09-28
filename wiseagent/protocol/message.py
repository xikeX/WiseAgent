"""
Author: Huang Weitao
Date: 2024-09-17 15:30:12
LastEditors: Huang Weitao
LastEditTime: 2024-09-26 23:25:29
Description: 
"""
from enum import Enum
from typing import Any, List

from pydantic import BaseModel

from wiseagent.config import logger

STREAM_END_FLAG = "[STREAM_END_FLAG]"


class MessageType(str, Enum):
    COMUNICATION = "communication"
    CONTROL = "control"
    THOUGHT = "thought"
    COMMAND = "command"


class Message(BaseModel):
    send_from: str = ""
    send_to: str = ""
    role: str = ""
    cause_by: str = ""
    content: str = ""
    time_stamp: str = ""
    message_type: MessageType = None
    appendix: dict = {}
    track: List[str] = []
    is_stream: bool = False
    # if is_stream is True, queue will be assigned a queue object
    stream_queue: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # To reduce the difficulty of identifying the intelligent agent, convert send_to, send_from to lowercase
        if self.send_to and any(char.isupper() for char in self.send_to):
            logger.warning(f"send_to {self.send_to} contains uppercase letters, convert to lowercase")
            self.send_to = self.send_to.lower()
        if self.send_from and any(char.isupper() for char in self.send_from):
            logger.warning(f"send_from {self.send_from} contains uppercase letters, convert to lowercase")
            self.send_from = self.send_from.lower()

    def add_image(self, image):
        # TODO: if image is a path, read it
        self.appendix["image"] = image

    def add_audio(self, audio):
        # TODO: if audio is a path, read it
        self.appendix["audio"] = audio

    @classmethod
    def transform(cls, message):
        """transfrom other message to normal message"""
        return cls(
            send_from=message.send_from,
            send_to=message.send_to,
            role=message.role,
            cause_by=message.cause_by,
            content=message.content,
            time_stamp=message.time_stamp,
            message_type=message.message_type,
            appendix=message.appendix,
            track=message.track,
        )


class AIMessage(Message):
    role: str = "asistant"
    # TODO: add more fields


class UserMessage(Message):
    role: str = "USER"
    # TODO: add more fields


class ThoughtMessage(Message):
    message_type: MessageType = MessageType.THOUGHT
