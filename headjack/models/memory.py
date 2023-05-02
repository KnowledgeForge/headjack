from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from chromadb.utils import embedding_functions
from headjack_server.config import get_chroma_client

if TYPE_CHECKING:
    from headjack_server.models.utterance import Utterance


@dataclass
class VectorStore:
    collection_name: str

    def __post_init__(self):
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.client = get_chroma_client()
        self.collection = self.client.get_or_create_collection(self.collection_name, embedding_function=ef)


@dataclass
class VectorStoreMemory:
    utterance: Optional[Utterance] = None
    vector_store: Optional[VectorStore] = None
    default_k: int = 3


#     @property
#     def session_id(self) -> Optional[UUID]:
#         return self.utterance and self.utterance.session_id

#     async def add_memories(self, utterances: List[Utterance]):
#         for utterance in utterances:
#             if self.session_id is not None and utterance.session_id != self.session_id:
#                 raise Exception("utterances belong to the same session as this memory!")
#         if self.vector_store is None:
#             self.vector_store = VectorStore(str(self.session_id))
#         await self.vector_store.coll

#     async def search(self, query: str, k: Optional[int] = None):
#         k = k or self.default_k
