import os


class EmbeddingFactory:
    @staticmethod
    def get_embedding(llm_type=None, api_key=None, base_url=None, model_name=None):
        llm_type = llm_type or os.environ.get("EMBEDDING_LLM_TYPE", None)
        api_key = api_key or os.environ.get("EMBEDDING_API_KEY", None)
        base_url = base_url or os.environ.get("EMBEDDING_BASE_URL", None)
        model_name = model_name or os.environ.get("EMBEDDING_MODEL_NAME", None)
        if not llm_type:
            raise ValueError("llm_type is required")
        if llm_type == "OpenAI":
            from wiseagent.tools.embedding.openai_embedding import OpenAIEmbedding

            return OpenAIEmbedding(api_key, base_url, model_name)
        # TODO: add other embedding types
        else:
            raise ValueError(f"Unsupported llm_type: {llm_type}")
