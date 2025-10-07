"""Tests for messages router."""

import json
import pytest
from fastapi.testclient import TestClient


def test_send_message(client: TestClient, sample_chat_data, sample_message_data):
    """Test sending a message to a chat via SSE endpoint."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]

    # Send a message via SSE endpoint
    with client.stream("POST", f"/chats/{chat_id}/messages/stream", json=sample_message_data) as r:
        assert r.status_code == 200
        # Consume the stream to completion to ensure server processed it
        for line in r.iter_lines():
            if not line:
                continue
            assert line.startswith("data: ")
            _payload = json.loads(line[len("data: "):])
            # We don't rely on chunk content here; just ensure streaming works
            if _payload.get("is_final"):
                break

    # Verify the messages endpoint responds with expected structure
    get_resp = client.get(f"/chats/{chat_id}/messages")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "messages" in data


def test_send_message_to_nonexistent_chat(client: TestClient, sample_message_data):
    """Test sending a message to a non-existent chat via SSE returns error event."""
    with client.stream("POST", "/chats/nonexistent-id/messages/stream", json=sample_message_data) as r:
        assert r.status_code == 200  # SSE stream returns 200 and streams error payload
        saw_error = False
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                payload = json.loads(line[len("data: "):])
                if "error" in payload:
                    saw_error = True
                    break
        assert saw_error


def test_reply_to_message_streams_error_for_nonexistent_message(
    client: TestClient, sample_chat_data, sample_reply_data
):
    """Replying to a nonexistent message streams an error event."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]

    # Ensure reply payload contains a parent_id field as required by schema
    reply_payload = {
        **sample_reply_data,
        "reply_metadata": {
            **sample_reply_data["reply_metadata"],
            "parent_id": "nonexistent-message-id",
        },
    }

    with client.stream(
        "POST",
        f"/chats/{chat_id}/messages/nonexistent-message-id/reply/stream",
        json=reply_payload,
    ) as r:
        assert r.status_code == 200
        saw_error = False
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith("data: "):
                payload = json.loads(line[len("data: "):])
                if payload.get("error"):
                    saw_error = True
                    break
        assert saw_error


def test_get_chat_messages(client: TestClient, sample_chat_data, sample_message_data):
    """Test getting all messages in a chat."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]

    # Send multiple messages via SSE
    for i in range(3):
        message_data = {**sample_message_data, "content": f"Message {i}"}
        with client.stream("POST", f"/chats/{chat_id}/messages/stream", json=message_data) as r:
            assert r.status_code == 200
            for line in r.iter_lines():
                if not line:
                    continue
                if line.startswith("data: ") and json.loads(line[len("data: "):]).get("is_final"):
                    break

    # Get all messages
    response = client.get(f"/chats/{chat_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data


    # Specific-message retrieval can't be tested without an ID-returning create endpoint.


def test_get_nonexistent_message(client: TestClient, sample_chat_data):
    """Test getting a non-existent message."""
    # Create a chat first
    chat_response = client.post("/chats/", json=sample_chat_data)
    chat_id = chat_response.json()["id"]
    
    response = client.get(f"/chats/{chat_id}/messages/nonexistent-id")
    assert response.status_code == 404

