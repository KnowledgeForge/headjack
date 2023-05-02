import urllib.parse
from dataclasses import dataclass

import requests

from headjack_server.models.tool import Tool, ToolSchema
from headjack_server.models.utterance import Action, Observation


@dataclass
class KnowledgeSearchTool(Tool):
    default_description = "Search for knowledge documents."
    default_ref_name = "knowledge_search"
    input_schema = ToolSchema("KnowledgeQueryActionSchema", {"query": str})
    n_docs: int = 3
    threshold: float = 0.0

    async def __call__(self, action: Action) -> Observation:
        # query = action.utterance_["query"]
        # results = knowledge_vectorstore.collection.query(query_texts=query, n_results=self.n_docs)
        # #         res = ""
        # #         for meta, doc in zip(results["metadatas"], results["documents"]):
        # #             res += f"{meta}: {doc}\n"
        # return Observation(tool=self, utterance_=results["documents"])
        return Observation(tool=self, utterance_="There were lots of profits")
