import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel

from wiseagent.common.logs import logger
from wiseagent.common.singleton import singleton

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("The 'chromadb' library is required. Please install it using 'pip install chromadb'.")


class MemoryItem(BaseModel):
    id: str
    score: Optional[float] = None
    metadatas: Optional[Dict] = None


@singleton
class ChromaDataBaseManager:
    def __init__(
        self,
        client: Optional[chromadb.Client] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
    ):
        """
        Initialize the Chromadb vector store.

        Args:
            client (chromadb.Client, optional): Existing chromadb client instance. Defaults to None.
            host (str, optional): Host address for chromadb server. Defaults to None.
            port (int, optional): Port for chromadb server. Defaults to None.
            path (str, optional): Path for local chromadb database. Defaults to None.
        """
        if client:
            self.client = client
        else:
            self.settings = Settings(anonymized_telemetry=False)

            if host and port:
                self.settings.chroma_server_host = host
                self.settings.chroma_server_http_port = port
                self.settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"
            else:
                if path is None:
                    path = "db"
            self.settings.persist_directory = path
            self.settings.is_persistent = True

            self.client = chromadb.Client(self.settings)
        self.collection_map: dict[str, chromadb.Collection] = {}

    def _parse_output(self, data: Dict) -> List[MemoryItem]:
        """Get the list of MemoryItem from the chromadb output.
        Args:
            data (Dict): The chromadb output.
        Returns:
            List[MemoryItem]: The list of MemoryItem.
        """
        ids = data.get("ids", [[]])[0]
        distances = data.get("distances", [[]])[0]
        metadatas = data.get("metadatas", [[]])[0]
        max_length = max(len(ids), len(distances), len(metadatas))
        res = [MemoryItem(id=ids[i], score=distances[i], metadatas=metadatas[i]) for i in range(max_length)]
        return res

    def get_or_create_collection(self, name: str, embedding_fn: Optional[callable] = None):
        """
        Create a new collection.

        Args:
            name (str): Name of the collection.
            embedding_fn (Optional[callable]): Embedding function to use. Defaults to None.

        Returns:
            chromadb.Collection: The created or retrieved collection.
        """
        collection = self.client.get_or_create_collection(
            name=name,
            embedding_function=embedding_fn,
        )
        self.collection_map[name] = collection
        return collection

    def add(
        self,
        collection_name: str,
        vectors: List[list],
        metadatas: List[Dict],
        ids: List[str] = None,
    ):
        """
        Add vectors into a collection.
        Args:
            collection_name (str): Name of the collection.
            vectors (List[list]): List of vectors to insert.
            metadatas (List[Dict]): List of metadata to insert.
            ids (List[str], optional): List of IDs to insert. Defaults to None.
        """
        if collection_name not in self.collection_map:
            self.collection_map[collection_name] = self.get_or_create_collection(collection_name)
        collection = self.collection_map[collection_name]
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        collection.add(ids=ids, embeddings=vectors, metadatas=metadatas)

    def search(
        self, collection_name: str, query_embeddings: List[int], limit: int = 5, filters: Optional[Dict] = None
    ) -> List[MemoryItem]:
        """
        Search for similar vectors.

        Args:
            collection_name (str): Name of the collection to search in.
            query_embeddings (List[int]): List of query embeddings.
            limit (int, optional): Number of results to return. Defaults to 5.
            filters (Optional[Dict], optional): Filters to apply. Defaults to None.
        Returns:
            List[MemoryItem]: The list of MemoryItem.
        """
        if collection_name not in self.collection_map:
            self.collection_map[collection_name] = self.get_or_create_collection(collection_name)
            logger.info(f"Created collection {collection_name}")
        collection = self.collection_map[collection_name]
        results = collection.query(query_embeddings=query_embeddings, where=filters, n_results=limit)
        final_results = self._parse_output(results)
        return final_results

    def delete(self, collection_name: str, ids: str):
        """
        Delete a vector by ID.

        Args:
            vector_id (str): ID of the vector to delete.
        """
        if collection_name not in self.collection_map:
            logger.info(f"Collection {collection_name} does not exist.")
            return False
        collection = self.collection_map[collection_name]
        collection.delete(ids=ids)
        return True

    def update(
        self,
        collection_name: str,
        id: str,
        vector: Optional[List[float]] = None,
        metadatas: Optional[Dict] = None,
    ):
        """
        Update a vector and its metadatas.

        Args:
            collection_name (str): Name of the collection to update.
            vector_id (str): ID of the vector to update.
            vector (Optional[List[float]], optional): Updated vector. Defaults to None.
            metadatas (Optional[Dict], optional): Updated metadatas. Defaults to None.
        """
        if collection_name not in self.collection_map:
            logger.info(f"Collection {collection_name} does not exist.")
            return
        collection = self.collection_map[collection_name]
        collection.update(ids=id, embeddings=vector, metadatas=metadatas)

    def get(self, collection_name: str, vector_id: str) -> MemoryItem:
        """
        Retrieve a vector by ID.

        Args:
            collection_name (str): Name of the collection to retrieve from.
            vector_id (str): ID of the vector to retrieve.

        Returns:
            MemoryItem: Retrieved vector.
        """
        if collection_name not in self.collection_map:
            self.collection_map[collection_name] = self.get_or_create_collection(collection_name)
        collection = self.collection_map[collection_name]
        result = collection.get(ids=[vector_id])
        return self._parse_output(result)[0]

    def list_cols(self) -> List[chromadb.Collection]:
        """
        List all collections.

        Returns:
            List[chromadb.Collection]: List of collections.
        """
        return self.client.list_collections()

    def delete_col(self, collection_name):
        """
        Delete a collection.
        """
        self.client.delete_collection(name=collection_name)

    def list(self, collection_name: str, filters: Optional[Dict] = None, limit: int = 100) -> List[MemoryItem]:
        """
        List all vectors in a collection.

        Args:
            collection_name (str): Name of the collection to list.
            filters (Optional[Dict], optional): Filters to apply to the list. Defaults to None.
            limit (int, optional): Number of vectors to return. Defaults to 100.

        Returns:
            List[MemoryItem]: List of vectors.
        """
        if collection_name not in self.collection_map:
            logger.info(f"Collection {collection_name} does not exist.")
            return
        collection = self.collection_map[collection_name]
        results = collection.get(where=filters, limit=limit)
        return [self._parse_output(results)]
