from dataclasses import dataclass, field
from typing import Dict, List
from uuid import uuid4

from chromadb.utils import embedding_functions

from headjack.config import get_chroma_client


@dataclass
class VectorStore:
    collection_name: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(self.collection_name, embedding_function=ef)

    def add(self, documents: List[str], metadatas: List[Dict[str, str]], ids: List[str]):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query: str, n: int = 1) -> dict[str, list]:
        return self.collection.query(query_texts=query, n_results=n)
