from dataclasses import dataclass

from chromadb.utils import embedding_functions
from headjack.config import get_chroma_client


@dataclass
class VectorStore:
    collection_name: str

    def __post_init__(self):
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(self.collection_name, embedding_function=ef)

