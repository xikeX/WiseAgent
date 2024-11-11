"""
Author: Huang Weitao
Date: 2024-09-21 10:17:05
LastEditors: Huang Weitao
LastEditTime: 2024-11-03 17:12:11
Description: 
"""
from typing import Any, List

from joblib import Memory

# from wiseagent.action.memory_action.base_memory_action import BaseMemoryAction
from wiseagent.action.base_action import BaseAction, BaseActionData
from wiseagent.common.protocol_command import ActionCommand
from wiseagent.common.protocol_message import (
    FileUploadMessage,
    SleepMessage,
    WakeupMessage,
    get_message_from_dict,
)
from wiseagent.common.singleton import singleton
from wiseagent.core.agent import Agent, get_current_agent_data
from wiseagent.tools.chroma_manager import ChromaDataBaseManager
from wiseagent.tools.embedding.base_embedding import BaseEmbedding
from wiseagent.tools.embedding.embedding_factory import EmbeddingFactory


class LongTermMemoryActionData(BaseActionData):
    model_config: dict = {"arbitrary_types_allowed": True}
    short_term_memory_threshold: int = 10  # TODO: This should be a configuration item
    chroma_db_manager: Any = None
    collection_name: str = None
    embedding_model: BaseEmbedding = None

    def __init__(self, agent_data: Agent, **kwargs):
        super().__init__(**kwargs)
        action_config = agent_data.get_action_config("MemoryAction")
        self.collection_name = action_config.get("collection_name", str(agent_data.id) + "long_term_memory")
        self.chroma_db_manager = ChromaDataBaseManager()
        self.embedding_model = EmbeddingFactory.get_embedding(agent_data.embedding_config)


@singleton
class LongTermMemoryAction(BaseAction):
    action_description: str = "Actions to manage long term memory"

    def check_start(self, command_list: List[ActionCommand] = None):
        """If the short term memory is more than the threshold, start the long term memory action"""
        agent_data: Agent = get_current_agent_data()
        action_data: LongTermMemoryActionData = agent_data.get_action_data(self.action_name)

        if agent_data.short_term_memory.size() > action_data.short_term_memory_threshold:
            # update the long term memory
            self.update_long_term_memory(agent_data)

    def init_agent(self, agent_data: Agent):
        agent_data.set_action_data(self.action_name, LongTermMemoryActionData(agent_data=agent_data))
        pass

    def update_long_term_memory(self, agent_data: Agent):
        # remove the exceeding short term memory
        action_data: LongTermMemoryActionData = agent_data.get_action_data(self.action_name)
        oldest_memory = agent_data.short_term_memory[-action_data.short_term_memory_threshold :]
        agent_data.set_short_term_memory(oldest_memory)
        # add the short term memory to the long term memory
        exclude_memory_type = [FileUploadMessage, SleepMessage, WakeupMessage]
        for memory in oldest_memory:
            if all(not isinstance(memory, mem_type) for mem_type in exclude_memory_type):
                self.add_memory(memory)

    def get_memory_store(self, **kwargs):
        """"""
        pass

    def clear_memory(self, oldest_k: int = 10):
        pass

    def get_memory(self, memory_id):
        action_data = get_current_agent_data().get_action_data(self.action_name)
        memory = action_data.chroma_db_manager.get(colletion_name=action_data.collection_name, id=memory_id)
        return get_message_from_dict(memory.metadata)

    def search(self, query, return_detail: bool = False) -> List[Memory]:
        action_data = get_current_agent_data().get_action_data(self.action_name)
        vectors = action_data.embedding_model.embed(query)
        memory_list = action_data.chroma_db_manager.search(
            colletion_name=action_data.collection_name, vectors=vectors, top_k=10
        )
        res = []
        for item in memory_list:
            memory = get_message_from_dict(item.metadata)
            if return_detail:
                res.append({"id": item.id, "score": item.score, "memory": memory})
            else:
                res.append(memory)
        return res

    def get_memory_list(self, last_k: int = 10):
        pass

    def add_memory(self, memory):
        key_content = memory.content
        vectors = self.embedding_model.embed(key_content)
        action_data: LongTermMemoryActionData = get_current_agent_data().get_action_data(self.action_name)
        action_data.chroma_db_manager.add(
            colletion_name=action_data.collection_name,
            vectors=vectors,
            metadatas=memory.to_dict(),
        )
