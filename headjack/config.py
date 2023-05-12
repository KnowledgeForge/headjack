"""
Module containing all config related things
"""
from typing import Iterator, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from pydantic import BaseSettings
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine
from functools import lru_cache


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
