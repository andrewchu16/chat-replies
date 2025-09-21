"""Tests for messages router."""

import pytest
from fastapi.testclient import TestClient


def test_send_message(client: TestClient, sample_chat_data, sample_message_data):
    """Test sending a message to a chat."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    # Send a message
    response = client.post(f"/chats/{chat_id}/messages", json=sample_message_data)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == sample_message_data["content"]
    assert data["sender"] == sample_message_data["sender"]
    assert data["chat_id"] == chat_id
    assert "id" in data
    assert "created_at" in data


def test_send_message_to_nonexistent_chat(client: TestClient, sample_message_data):
    """Test sending a message to a non-existent chat."""
    response = client.post("/chats/nonexistent-id/messages", json=sample_message_data)
    assert response.status_code == 404


def test_reply_to_message(client: TestClient, sample_chat_data, sample_message_data, sample_reply_data):
    """Test replying to a message."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    # Send an initial message
    message_response = client.post(f"/chats/{chat_id}/messages", json=sample_message_data)
    message_id = message_response.json()["id"]
    
    # Reply to the message
    response = client.post(f"/chats/{chat_id}/messages/{message_id}/reply", json=sample_reply_data)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == sample_reply_data["content"]
    assert data["sender"] == sample_reply_data["sender"]
    assert data["chat_id"] == chat_id
    assert len(data["reply_metadata"]) == 1


def test_get_chat_messages(client: TestClient, sample_chat_data, sample_message_data):
    """Test getting all messages in a chat."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    # Send multiple messages
    for i in range(3):
        message_data = {**sample_message_data, "content": f"Message {i}"}
        client.post(f"/chats/{chat_id}/messages", json=message_data)
    
    # Get all messages
    response = client.get(f"/chats/{chat_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["messages"]) == 3


def test_get_specific_message(client: TestClient, sample_chat_data, sample_message_data):
    """Test getting a specific message by ID."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    # Send a message
    message_response = client.post(f"/chats/{chat_id}/messages", json=sample_message_data)
    message_id = message_response.json()["id"]
    
    # Get the specific message
    response = client.get(f"/chats/{chat_id}/messages/{message_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["content"] == sample_message_data["content"]


def test_get_nonexistent_message(client: TestClient, sample_chat_data):
    """Test getting a non-existent message."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    response = client.get(f"/chats/{chat_id}/messages/nonexistent-id")
    assert response.status_code == 404
