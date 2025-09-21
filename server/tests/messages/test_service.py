"""Tests for messages service."""

import pytest
from sqlalchemy.orm import Session

from src.messages.service import MessageService
from src.messages.schemas import MessageCreate, MessageReply, MessageReplyMetadataCreate
from src.chats.service import ChatService
from src.chats.schemas import ChatCreate
from src.exceptions import MessageNotFoundError, ChatNotFoundError, InvalidReplyRangeError
from src.models import SenderType


def test_create_message(db: Session):
    """Test creating a message."""
    # Create a chat first
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create a message
    message_service = MessageService(db)
    message_data = MessageCreate(content="Test message", sender=SenderType.USER)
    
    message = message_service.create_message(chat.id, message_data)
    
    assert message.content == "Test message"
    assert message.sender == SenderType.USER
    assert message.chat_id == chat.id
    assert message.id is not None


def test_create_message_in_nonexistent_chat(db: Session):
    """Test creating a message in a non-existent chat."""
    message_service = MessageService(db)
    message_data = MessageCreate(content="Test message", sender=SenderType.USER)
    
    with pytest.raises(ChatNotFoundError):
        message_service.create_message("nonexistent-id", message_data)


def test_reply_to_message(db: Session):
    """Test replying to a message."""
    # Create a chat and initial message
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    original_message = message_service.create_message(
        chat.id,
        MessageCreate(content="Original message", sender=SenderType.USER)
    )
    
    # Reply to the message
    reply_data = MessageReply(
        content="Reply message",
        sender=SenderType.AI,
        reply_metadata=MessageReplyMetadataCreate(start_index=0, end_index=8)
    )
    
    reply = message_service.reply_to_message(chat.id, original_message.id, reply_data)
    
    assert reply.content == "Reply message"
    assert reply.sender == SenderType.AI
    assert reply.chat_id == chat.id
    assert len(reply.reply_metadata) == 1
    assert reply.reply_metadata[0].start_index == 0
    assert reply.reply_metadata[0].end_index == 8


def test_reply_with_invalid_range(db: Session):
    """Test replying with invalid reply range."""
    # Create a chat and initial message
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    original_message = message_service.create_message(
        chat.id,
        MessageCreate(content="Short", sender=SenderType.USER)
    )
    
    # Reply with invalid range
    reply_data = MessageReply(
        content="Reply message",
        sender=SenderType.AI,
        reply_metadata=MessageReplyMetadataCreate(start_index=0, end_index=100)  # Beyond content length
    )
    
    with pytest.raises(InvalidReplyRangeError):
        message_service.reply_to_message(chat.id, original_message.id, reply_data)


def test_get_message(db: Session):
    """Test getting a message by ID."""
    # Create a chat and message
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    created_message = message_service.create_message(
        chat.id,
        MessageCreate(content="Test message", sender=SenderType.USER)
    )
    
    # Get the message
    retrieved_message = message_service.get_message(chat.id, created_message.id)
    
    assert retrieved_message.id == created_message.id
    assert retrieved_message.content == created_message.content


def test_get_nonexistent_message(db: Session):
    """Test getting a non-existent message."""
    # Create a chat
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    
    with pytest.raises(MessageNotFoundError):
        message_service.get_message(chat.id, "nonexistent-id")


def test_get_chat_messages(db: Session):
    """Test getting all messages in a chat."""
    # Create a chat
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages
    message_service = MessageService(db)
    for i in range(3):
        message_service.create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=SenderType.USER)
        )
    
    messages = message_service.get_chat_messages(chat.id)
    assert len(messages) == 3


def test_count_chat_messages(db: Session):
    """Test counting messages in a chat."""
    # Create a chat
    chat_service = ChatService(db)
    chat = chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages
    message_service = MessageService(db)
    for i in range(5):
        message_service.create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=SenderType.USER)
        )
    
    count = message_service.count_chat_messages(chat.id)
    assert count == 5
