"""
Tests for app.py
"""
from headjack_server.models import Document, KnowledgeDocument


def test_healthcheck(client):
    client.get("/healthcheck/")


def test_create_and_then_get_a_node_embedding(client):
    node = Document(**{"name": "foo", "description": "This is a description of node foo."})
    client.post("/nodes/", json=node.dict())
    response = client.get("nodes/foo/")
    assert response.status_code == 200
    assert response.json() == {
        "ids": ["foo"],
        "embeddings": None,
        "documents": ["placeholder sentence"],
        "metadatas": [{"node_document": "foo"}],
    }


def test_create_and_then_get_a_knowledge_embedding(client):
    knowledge = KnowledgeDocument(
        **{
            "name": "foo",
            "description": "This is a description of knowledge foo.",
            "content": "This is some content about knowledge foo.",
            "url": "https://www.example.com",
        }
    )
    client.post("/knowledge/", json=knowledge.dict())
    response = client.get("knowledge/foo/")
    assert response.status_code == 200
    assert response.json() == {
        "ids": ["foo"],
        "embeddings": None,
        "documents": ["placeholder sentence"],
        "metadatas": [{"knowledge_document": "foo"}],
    }
