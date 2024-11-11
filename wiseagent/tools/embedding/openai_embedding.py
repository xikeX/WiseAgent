import os
from typing import Optional

from openai import OpenAI

from wiseagent.tools.embedding.base_embedding import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str],
        model_name: Optional[str],
        embedding_dims: Optional[int] = None,
    ):
        super().__init__()

        self.embedding_dims = embedding_dims or 1024
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed(self, text):
        """
        Get the embedding for the given text using OpenAI.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        text = text.replace("\n", " ")
        return self.client.embeddings.create(input=[text], model=self.model_name).data[0].embedding
