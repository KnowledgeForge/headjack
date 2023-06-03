"""
Module containing all config related things
"""
import os
from functools import lru_cache
from typing import Optional

import chromadb
from pydantic import BaseSettings


@lru_cache(1)
def get_chroma_client():  # pragma: no cover
    """
    Get a chromadb client
    """
    return chromadb.Client()


class Settings(BaseSettings):
    """
    Headjack config

    Config values can be overriden by environment variables.
    Environment variables are expected to be prefixed by HEADJACK_, i.e. HEADJACK_METADATA_DB
    """

    metadata_db: str = "sqlite:///headjack.db?check_same_thread=False"
    port: Optional[int] = 8679
    search_service: Optional[str] = "http://localhost:16410"
    metric_service: Optional[str] = "http://localhost:8000"
    secret: Optional[str] = "headjack_secret"
    
    class Config:
        env_prefix = "headjack_"  # all environment variables wil use this prefix


def get_settings():
    return Settings()


def get_headjack_secret():
    return os.environ.get("HEADJACK_SECRET", get_settings().secret)

