"""
Module containing all config related things
"""
import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings


def get_chroma_client():  # pragma: no cover
    """
    Get a chromadb client
    """
    chroma_client = chromadb.Client(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host="chromadb",
            chroma_server_http_port="16402",
        ),
    )
    return chroma_client


def get_headjack_collection() -> Collection:  # pragma: no cover
    """
    Get the headjack collection
    """
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection("knowledge")
    return collection
