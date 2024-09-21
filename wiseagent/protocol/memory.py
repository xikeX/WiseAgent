"""
Author: Huang Weitao
Date: 2024-09-21 10:32:26
LastEditors: Huang Weitao
LastEditTime: 2024-09-21 10:32:34
Description: 
"""

from mailbox import Message


class Memory(Message):
    memory_id: str = ""
    memory_type: str = ""


class LongTermMemory(Memory):
    pass


class ShortTermMemory(Memory):
    pass


class KnowledgeBase(Memory):
    pass
