"""Tests for chats service."""

import pytest
from sqlalchemy.orm import Session

from src.chats.service import ChatService
from src.chats.schemas import ChatCreate, ChatUpdate
from src.exceptions import ChatNotFoundError


def test_create_chat(db: Session):
    """Test creating a chat."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Test Chat")
    
    chat = service.create_chat(chat_data)
    
    assert chat.title == "Test Chat"
    assert chat.id is not None
    assert chat.created_at is not None


def test_get_chat(db: Session):
    """Test getting a chat by ID."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Test Chat")
    
    created_chat = service.create_chat(chat_data)
    retrieved_chat = service.get_chat(created_chat.id)
    
    assert retrieved_chat.id == created_chat.id
    assert retrieved_chat.title == created_chat.title


def test_get_nonexistent_chat(db: Session):
    """Test getting a non-existent chat raises exception."""
    service = ChatService(db)
    
    with pytest.raises(ChatNotFoundError):
        service.get_chat("nonexistent-id")


def test_update_chat(db: Session):
    """Test updating a chat."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Original Title")
    
    created_chat = service.create_chat(chat_data)
    update_data = ChatUpdate(title="Updated Title")
    updated_chat = service.update_chat(created_chat.id, update_data)
    
    assert updated_chat.id == created_chat.id
    assert updated_chat.title == "Updated Title"


def test_update_nonexistent_chat(db: Session):
    """Test updating a non-existent chat raises exception."""
    service = ChatService(db)
    update_data = ChatUpdate(title="Updated Title")
    
    with pytest.raises(ChatNotFoundError):
        service.update_chat("nonexistent-id", update_data)


def test_list_chats(db: Session):
    """Test listing chats."""
    service = ChatService(db)
    
    # Create multiple chats
    for i in range(3):
        chat_data = ChatCreate(title=f"Chat {i}")
        service.create_chat(chat_data)
    
    chats = service.list_chats()
    assert len(chats) == 3
