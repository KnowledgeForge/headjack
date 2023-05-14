"""
Module containing all config related things
"""
import os
from functools import lru_cache
from typing import Iterator, Optional

import chromadb
from pydantic import BaseSettings
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine


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
    search_service: Optional[str] = None
    port: Optional[int] = 8679
    search_service: Optional[str] = "http://localhost:16410"
    metric_service: Optional[str] = "http://localhost:8000"

    class Config:
        env_prefix = "headjack_"  # all environment variables wil use this prefix


def get_settings():
    return Settings()


def get_engine() -> Engine:
    """
    Create the metadata engine.
    """
    settings = get_settings()
    engine = create_engine(settings.metadata_db)

    return engine


def get_session() -> Iterator[Session]:
    engine = get_engine()

    with Session(engine, autoflush=False) as session:  # pragma: no cover
        yield session


def get_headjack_secret():
    secret = os.environ.get("HEADJACK_SECRET", "headjack_secret")
    if not secret:
        raise EnvironmentError("HEADJACK_SECRET environment variable not found")
