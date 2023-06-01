"""
Headjack search service
"""
import argparse
import logging
from enum import Enum
from typing import List, Optional
from uuid import uuid4
import uvicorn

from chromadb.api import API
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from headjack_search_service.api.helpers import get_chroma_client, get_embedding_function
from headjack_search_service.api.models import Utterance, UtteranceType

_logger = logging.getLogger(__name__)

origins = ["*"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class COLLECTION_TYPE(str, Enum):
    knowledge = "knowledge"
    metrics = "metrics"
    messages = "messages"
    people = "people"

@app.get("/healthcheck")
@app.get("/healthcheck/", include_in_schema=False)
async def health_check(*, chroma_client: API = Depends(get_chroma_client)):
    _logger.info(f"Pinging chroma database...")
    chroma_client.heartbeat()
    _logger.info(f"Pinging successful")
    return {"status": "OK"}


@app.get("/query")
@app.get("/query/", include_in_schema=False)
async def query(text: str, collection: COLLECTION_TYPE, n: int = 3, *, chroma_client: API = Depends(get_chroma_client)):
    _logger.info(f"Connecting to collection for {collection.value}")
    chroma_collection = chroma_client.get_collection(collection.value)
    num_elements = chroma_collection.count()
    results = chroma_collection.query(query_texts=[text], n_results=n if n <= num_elements else num_elements)
    return results

@app.get("/count")
@app.get("/count/", include_in_schema=False)
async def get_number_of_documents(collection: COLLECTION_TYPE, *, chroma_client: API = Depends(get_chroma_client)) -> JSONResponse:
    _logger.info(f"Connecting to collection for {collection.value}")
    chroma_collection = chroma_client.get_collection(collection.value)
    return {
        "collection": collection,
        "count": chroma_collection.count()
    }

@app.post("/session/{session_id}")
@app.post("/session/{session_id}/", include_in_schema=False)
async def save_utterances_for_a_session(
    session_id: str, *, utterances: List[Utterance], chroma_client: API = Depends(get_chroma_client)
):
    _logger.info(f"Saving utterances for session {session_id}")
    chroma_collection = chroma_client.get_or_create_collection(
        "session_history",
        embedding_function=get_embedding_function(),
    )

    documents = []
    metadatas = []
    ids = []
    for utterance in utterances:
        documents.append(utterance.context)
        metadatas.append({"session_id": session_id, "timestamp": str(utterance.timestamp), "type": utterance.type.value})
        ids.append(str(uuid4()))
    chroma_collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    chroma_client.persist()
    return JSONResponse(
        status_code=201,
        content={
            "message": (f"Utterance successfully saved for session {session_id}"),
        },
    )


@app.get("/session/{session_id}")
@app.get("/session/{session_id}/", include_in_schema=False)
async def search_utterances_for_a_session(
    session_id: str, query: str, n: int = 3, type_: Optional[UtteranceType] = UtteranceType.user, *, chroma_client: API = Depends(get_chroma_client)
):
    _logger.info(f"Pulling utterances for session {session_id}")
    chroma_collection = chroma_client.get_or_create_collection(
        "session_history",
        embedding_function=get_embedding_function(),
    )
    num_elements = chroma_collection.count()
    try:
        results = chroma_collection.query(
            query_texts=[query], where={"session_id": session_id, "type": type_.value}, n_results=n if n <= num_elements else num_elements
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return results

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host")
    parser.add_argument("--port", help="Port", type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
