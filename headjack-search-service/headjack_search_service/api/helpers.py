"""
Module containing all config related things
"""
from functools import lru_cache
import logging
from pydantic import BaseSettings

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

_logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    hss_chroma_db_impl: str = "duckdb+parquet"
    hss_chroma_api_impl: str = "local"
    hss_chroma_host: str = "0.0.0.0"
    hss_chroma_port: int = 16411
    hss_chroma_persist_directory = "/Users/samredai/Workspaces/headjack-workspace/headjack-search-service/headjack-search-service-index"

def get_chroma_client():  # pragma: no cover
    """
    Get a chromadb client
    """
    settings = get_settings()
    chroma_client = chromadb.Client(
        ChromaSettings(
            chroma_db_impl=settings.hss_chroma_db_impl,
            chroma_api_impl=settings.hss_chroma_api_impl,
            chroma_server_host=settings.hss_chroma_host,
            chroma_server_http_port=settings.hss_chroma_port,
            persist_directory=settings.hss_chroma_persist_directory,
        )
    )
    return chroma_client


def get_collection(client: chromadb.Client, collection: str) -> Collection:
    """
    Get the headjack chroma collection
    """
    _logger.info(f"Getting chroma collection {collection}")
    return client.get_or_create_collection(collection)

@lru_cache(maxsize=1)
def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()