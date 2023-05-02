"""
Module containing all config related things
"""
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from pydantic import BaseSettings

CHROMA = None


def get_chroma_client():  # pragma: no cover
    """
    Get a chromadb client
    """
    global CHROMA
    if CHROMA is None:
        CHROMA = chromadb.Client(
            ChromaSettings(
                chroma_api_impl="rest",
                chroma_server_host="chromadb",
                chroma_server_http_port="16402",
            ),
        )
    return CHROMA


class Settings(BaseSettings):
    """
    Headjack config
    """

    metadata_db: str = "sqlite:///headjack.db?check_same_thread=False"
    search_service: Optional[str] = None

    class Config:
        env_prefix = "headjack_"  # all environment variables wil use this prefix


def get_settings():
    return Settings()
