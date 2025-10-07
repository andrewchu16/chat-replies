"""Tests for messages service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.messages.service import MessageService
from src.messages.schemas import MessageCreate, MessageReplyCreate, MessageReplyMetadataCreate
from src.chats.service import ChatService
from src.chats.schemas import ChatCreate
from src.exceptions import MessageNotFoundError, ChatNotFoundError
from src.messages.exceptions import InvalidReplyRangeError
from src.models import SenderType


@pytest.mark.asyncio
async def test_create_message(db: AsyncSession):
    """Test creating a message."""
    # Create a chat first
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create a message
    message_service = MessageService(db)
    message_data = MessageCreate(content="Test message", sender=SenderType.USER)
    
    message = await message_service._create_message(chat.id, message_data)
    
    assert message.content == "Test message"
    assert message.sender == SenderType.USER
    assert message.chat_id == chat.id
    assert message.id is not None


@pytest.mark.asyncio
async def test_create_message_in_nonexistent_chat(db: AsyncSession):
    """Test creating a message in a non-existent chat."""
    message_service = MessageService(db)
    message_data = MessageCreate(content="Test message", sender=SenderType.USER)
    
    with pytest.raises(ChatNotFoundError):
        await message_service._create_message("nonexistent-id", message_data)


@pytest.mark.asyncio
async def test_reply_to_message(db: AsyncSession):
    """Test replying to a message."""
    # Create a chat and initial message
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    original_message = await message_service._create_message(
        chat.id,
        MessageCreate(content="Original message", sender=SenderType.USER)
    )
    
    # Reply to the message
    reply_data = MessageReplyCreate(
        content="Reply message",
        sender=SenderType.AI,
        reply_metadata=MessageReplyMetadataCreate(start_index=0, end_index=8, parent_id=original_message.id)
    )
    
    reply = await message_service._create_message_reply(chat.id, original_message.id, reply_data)
    
    assert reply.content == "Reply message"
    assert reply.sender == SenderType.AI
    assert reply.chat_id == chat.id
    
    # We need to fetch the reply metadata separately to avoid lazy loading issues
    # This is acceptable for the test but in production we might want to use selectinload or joinedload
    await db.refresh(reply, ["reply_metadata"])
    assert len(reply.reply_metadata) == 1
    assert reply.reply_metadata[0].start_index == 0
    assert reply.reply_metadata[0].end_index == 8


@pytest.mark.asyncio
async def test_reply_with_invalid_range(db: AsyncSession):
    """Test replying with invalid reply range."""
    # Create a chat and initial message
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    original_message = await message_service._create_message(
        chat.id,
        MessageCreate(content="Short", sender=SenderType.USER)
    )
    
    # Reply with invalid range
    reply_data = MessageReplyCreate(
        content="Reply message",
        sender=SenderType.AI,
        reply_metadata=MessageReplyMetadataCreate(start_index=0, end_index=100, parent_id=original_message.id)  # Beyond content length
    )
    
    with pytest.raises(InvalidReplyRangeError):
        await message_service._create_message_reply(chat.id, original_message.id, reply_data)


@pytest.mark.asyncio
async def test_get_message(db: AsyncSession):
    """Test getting a message by ID."""
    # Create a chat and message
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    created_message = await message_service._create_message(
        chat.id,
        MessageCreate(content="Test message", sender=SenderType.USER)
    )
    
    # Get the message
    retrieved_message = await message_service.get_message(chat.id, created_message.id)
    
    assert retrieved_message.id == created_message.id
    assert retrieved_message.content == created_message.content


@pytest.mark.asyncio
async def test_get_nonexistent_message(db: AsyncSession):
    """Test getting a non-existent message."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    
    with pytest.raises(MessageNotFoundError):
        await message_service.get_message(chat.id, "nonexistent-id")


@pytest.mark.asyncio
async def test_get_chat_messages(db: AsyncSession):
    """Test getting all messages in a chat."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages
    message_service = MessageService(db)
    for i in range(3):
        await message_service._create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=SenderType.USER)
        )
    
    messages = await message_service.get_chat_messages(chat.id)
    assert len(messages) == 3


@pytest.mark.asyncio
async def test_count_chat_messages(db: AsyncSession):
    """Test counting messages in a chat."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages
    message_service = MessageService(db)
    for i in range(5):
        await message_service._create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=SenderType.USER)
        )
    
    count = await message_service.count_chat_messages(chat.id)
    assert count == 5
