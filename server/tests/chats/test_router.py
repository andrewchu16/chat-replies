"""Tests for chats router."""

import pytest
from fastapi.testclient import TestClient


def test_create_chat(client: TestClient, sample_chat_data):
    """Test creating a new chat."""
    response = client.post("/chats/", json=sample_chat_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_chat_data["title"]
    assert "id" in data
    assert "created_at" in data


def test_get_chat(client: TestClient, sample_chat_data):
    """Test getting a chat by ID."""
    # Create a chat first
    create_response = client.post("/chats/", json=sample_chat_data)
    chat_id = create_response.json()["id"]
    
    # Get the chat
    response = client.get(f"/chats/{chat_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == chat_id
    assert data["title"] == sample_chat_data["title"]


def test_get_nonexistent_chat(client: TestClient):
    """Test getting a non-existent chat."""
    response = client.get("/chats/nonexistent-id")
    assert response.status_code == 404


def test_update_chat(client: TestClient, sample_chat_data):
    """Test updating a chat."""
    # Create a chat first
    create_response = client.post("/chats/", json=sample_chat_data)
    chat_id = create_response.json()["id"]
    
    # Update the chat
    update_data = {"title": "Updated Chat Title"}
    response = client.put(f"/chats/{chat_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["id"] == chat_id


def test_update_nonexistent_chat(client: TestClient):
    """Test updating a non-existent chat."""
    update_data = {"title": "Updated Chat Title"}
    response = client.put("/chats/nonexistent-id", json=update_data)
    assert response.status_code == 404

