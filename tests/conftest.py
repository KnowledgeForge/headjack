"""
Global test fixtures
"""
from typing import Iterator

import chromadb
import pytest
from chromadb.api.local import LocalAPI
from chromadb.api.models import Collection
from fastapi.testclient import TestClient

from headjack_server.api.app import app
from headjack_server.config import get_chroma_client, get_headjack_collection


@pytest.fixture
def chroma_client() -> LocalAPI:
    """
    Create an in-memory SQLite session to test models.
    """
    client = chromadb.Client()
    yield client


@pytest.fixture
def headjack_collection() -> Collection:
    """
    Create an in-memory SQLite session to test models.
    """
    client = chromadb.Client()
    headjack_collection = client.get_or_create_collection("headjack")
    yield headjack_collection


@pytest.fixture
def client(chroma_client: LocalAPI, headjack_collection: Collection) -> Iterator[TestClient]:
    """
    Test rest client
    """

    def get_chroma_client_override() -> LocalAPI:
        return chroma_client

    def get_headjack_collection_override() -> LocalAPI:
        return headjack_collection

    app.dependency_overrides[get_chroma_client] = get_chroma_client_override
    app.dependency_overrides[get_headjack_collection] = get_headjack_collection_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
