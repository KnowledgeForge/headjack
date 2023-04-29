from dataclasses import dataclass
from itertools import chain
from typing import (
    TypedDict,
)

import chromadb
import lmql
import pandas as pd
import requests
from chromadb.utils import embedding_functions


@dataclass
class KnowledgeSearchTool(Tool):
    default_description = "Search for knowledge documents."
    default_ref_name = "knowledge_search"
    input_schema = ToolSchema(TypedDict("KnowledgeQuery", {"query": str}))
    n_docs: int = 3
    threshold: float = 0.0

    async def __call__(self, action: Action) -> Observation:
        query = action.utterance_["query"]
        results = knowledge_vectorstore.collection.query(query_texts=query, n_results=self.n_docs)
        #         res = ""
        #         for meta, doc in zip(results["metadatas"], results["documents"]):
        #             res += f"{meta}: {doc}\n"
        return Observation(tool=self, utterance_=results["documents"])
