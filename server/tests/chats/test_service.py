"""Tests for chats service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.chats.service import ChatService
from src.chats.schemas import ChatCreate, ChatUpdate
from src.exceptions import ChatNotFoundError


@pytest.mark.asyncio
async def test_create_chat(db: AsyncSession):
    """Test creating a chat."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Test Chat")
    
    chat = await service.create_chat(chat_data)
    
    assert chat.title == "Test Chat"
    assert chat.id is not None
    assert chat.created_at is not None


@pytest.mark.asyncio
async def test_get_chat(db: AsyncSession):
    """Test getting a chat by ID."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Test Chat")
    
    created_chat = await service.create_chat(chat_data)
    retrieved_chat = await service.get_chat(created_chat.id)
    
    assert retrieved_chat.id == created_chat.id
    assert retrieved_chat.title == created_chat.title
    assert retrieved_chat.created_at == created_chat.created_at


@pytest.mark.asyncio
async def test_get_nonexistent_chat(db: AsyncSession):
    """Test getting a non-existent chat raises exception."""
    service = ChatService(db)
    
    with pytest.raises(ChatNotFoundError):
        await service.get_chat("nonexistent-id")


@pytest.mark.asyncio
async def test_update_chat(db: AsyncSession):
    """Test updating a chat."""
    service = ChatService(db)
    chat_data = ChatCreate(title="Original Title")
    
    created_chat = await service.create_chat(chat_data)
    update_data = ChatUpdate(title="Updated Title")
    updated_chat = await service.update_chat(created_chat.id, update_data)
    
    assert updated_chat.id == created_chat.id
    assert updated_chat.title == "Updated Title"


@pytest.mark.asyncio
async def test_update_nonexistent_chat(db: AsyncSession):
    """Test updating a non-existent chat raises exception."""
    service = ChatService(db)
    update_data = ChatUpdate(title="Updated Title")
    
    with pytest.raises(ChatNotFoundError):
        await service.update_chat("nonexistent-id", update_data)


@pytest.mark.asyncio
async def test_list_chats(db: AsyncSession):
    """Test listing chats."""
    service = ChatService(db)
    
    # Create multiple chats
    for i in range(3):
        chat_data = ChatCreate(title=f"Chat {i}")
        await service.create_chat(chat_data)
    
    chats, total = await service.list_chats()
    print(chats)
    assert len(chats) == 3
    assert total == 3
    assert chats[0].title == "Chat 2"
    assert chats[1].title == "Chat 1"
    assert chats[2].title == "Chat 0"
