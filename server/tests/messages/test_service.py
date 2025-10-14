"""Tests for messages service."""

import asyncio
import pytest
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


@pytest.mark.asyncio
async def test_get_chat_messages_ascending_order(db: AsyncSession):
    """Test that messages are retrieved in ascending chronological order (oldest first)."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages with different senders
    message_service = MessageService(db)
    messages = []
    for i in range(5):
        sender = SenderType.USER if i % 2 == 0 else SenderType.AI
        message = await message_service._create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=sender)
        )
        messages.append(message)
    
    # Get messages in ascending order (default)
    retrieved_messages = await message_service.get_chat_messages(chat.id, reverse=False)
    
    # Verify we got all messages
    assert len(retrieved_messages) == 5
    
    # Verify messages are in ascending chronological order (oldest first)
    for i in range(len(retrieved_messages) - 1):
        current_created_at = retrieved_messages[i].created_at
        next_created_at = retrieved_messages[i + 1].created_at
        assert current_created_at <= next_created_at, f"Message {i} should be older than message {i+1}"
    
    # Verify content matches expected order
    for i, message in enumerate(retrieved_messages):
        assert message.content == f"Message {i}"


@pytest.mark.asyncio
async def test_get_chat_messages_descending_order(db: AsyncSession):
    """Test that messages are retrieved in descending chronological order (newest first)."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create multiple messages
    message_service = MessageService(db)
    messages = []
    for i in range(5):
        message = await message_service._create_message(
            chat.id,
            MessageCreate(content=f"Message {i}", sender=SenderType.USER)
        )
        messages.append(message)
    
    # Get messages in descending order
    retrieved_messages = await message_service.get_chat_messages(chat.id, reverse=True)
    
    # Verify we got all messages
    assert len(retrieved_messages) == 5
    
    # Verify messages are in descending chronological order (newest first)
    for i in range(len(retrieved_messages) - 1):
        current_created_at = retrieved_messages[i].created_at
        next_created_at = retrieved_messages[i + 1].created_at
        assert current_created_at > next_created_at, f"Message {i} should be newer than message {i+1}"
    
    # Verify content matches expected reverse order
    for i, message in enumerate(retrieved_messages):
        expected_content = f"Message {4 - i}"  # Reverse order: 4, 3, 2, 1, 0
        assert message.content == expected_content


@pytest.mark.asyncio
async def test_get_chat_messages_order_with_replies(db: AsyncSession):
    """Test message ordering when messages have replies."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    
    # Create first message
    message1 = await message_service._create_message(
        chat.id,
        MessageCreate(content="First message", sender=SenderType.USER)
    )
    
    message2 = await message_service._create_message(
        chat.id,
        MessageCreate(content="Second message", sender=SenderType.AI)
    )
    
    # Create a reply to the original message
    reply_data = MessageReplyCreate(
        content="Reply message",
        sender=SenderType.USER,
        reply_metadata=MessageReplyMetadataCreate(start_index=0, end_index=8, parent_id=message2.id)
    )
    await message_service._create_message_reply(chat.id, message2.id, reply_data)
    
    # Create another message after the reply
    await message_service._create_message(
        chat.id,
        MessageCreate(content="Final message", sender=SenderType.USER)
    )
    
    # Get messages in ascending order
    retrieved_messages = await message_service.get_chat_messages(chat.id, reverse=False)
    
    # Verify we got all 3 messages
    assert len(retrieved_messages) == 4
    
    # Verify chronological order: first -> second -> reply -> final
    assert retrieved_messages[0].content == "First message"
    assert retrieved_messages[1].content == "Second message"
    assert retrieved_messages[2].content == "Reply message"
    assert retrieved_messages[3].content == "Final message"
    
    # Verify timestamps are in ascending order
    for i in range(len(retrieved_messages) - 1):
        current_created_at = retrieved_messages[i].created_at
        next_created_at = retrieved_messages[i + 1].created_at
        assert current_created_at <= next_created_at


@pytest.mark.asyncio
async def test_get_chat_messages_order_with_pagination(db: AsyncSession):
    """Test message ordering with pagination."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    # Create 10 messages
    message_service = MessageService(db)
    for i in range(10):
        await message_service._create_message(
            chat.id,
            MessageCreate(content=f"Message {i:02d}", sender=SenderType.USER)
        )
    
    # Test pagination with ascending order
    page1 = await message_service.get_chat_messages(chat.id, skip=0, limit=5, reverse=False)
    page2 = await message_service.get_chat_messages(chat.id, skip=5, limit=5, reverse=False)
    
    # Verify page 1 contains messages 0-4 in order
    assert len(page1) == 5
    for i, message in enumerate(page1):
        assert message.content == f"Message {i:02d}"
    
    # Verify page 2 contains messages 5-9 in order
    assert len(page2) == 5
    for i, message in enumerate(page2):
        assert message.content == f"Message {i+5:02d}"
    
    # Verify timestamps are in ascending order within each page
    for page in [page1, page2]:
        for i in range(len(page) - 1):
            assert page[i].created_at <= page[i + 1].created_at
    
    # Test pagination with descending order
    page1_desc = await message_service.get_chat_messages(chat.id, skip=0, limit=5, reverse=True)
    page2_desc = await message_service.get_chat_messages(chat.id, skip=5, limit=5, reverse=True)
    
    # Verify page 1 contains messages 9-5 in descending order
    assert len(page1_desc) == 5
    for i, message in enumerate(page1_desc):
        assert message.content == f"Message {9-i:02d}"
    
    # Verify page 2 contains messages 4-0 in descending order
    assert len(page2_desc) == 5
    for i, message in enumerate(page2_desc):
        assert message.content == f"Message {4-i:02d}"


@pytest.mark.asyncio
async def test_get_chat_messages_order_mixed_senders(db: AsyncSession):
    """Test message ordering with mixed USER and AI senders."""
    # Create a chat
    chat_service = ChatService(db)
    chat = await chat_service.create_chat(ChatCreate(title="Test Chat"))
    
    message_service = MessageService(db)
    
    # Create a conversation with alternating senders
    conversation = [
        ("Hello", SenderType.USER),
        ("Hi there!", SenderType.AI),
        ("How are you?", SenderType.USER),
        ("I'm doing well, thanks!", SenderType.AI),
        ("That's great!", SenderType.USER),
    ]
    
    created_messages = []
    for content, sender in conversation:
        message = await message_service._create_message(
            chat.id,
            MessageCreate(content=content, sender=sender)
        )
        created_messages.append(message)
    
    # Get messages in ascending order
    retrieved_messages = await message_service.get_chat_messages(chat.id, reverse=False)
    
    # Verify we got all messages
    assert len(retrieved_messages) == len(conversation)
    
    # Verify messages are in chronological order regardless of sender
    for i in range(len(retrieved_messages) - 1):
        current_created_at = retrieved_messages[i].created_at
        next_created_at = retrieved_messages[i + 1].created_at
        assert current_created_at <= next_created_at
    
    # Verify content and sender match expected conversation
    for i, (expected_content, expected_sender) in enumerate(conversation):
        assert retrieved_messages[i].content == expected_content
        assert retrieved_messages[i].sender == expected_sender
    
    # Test descending order
    retrieved_messages_desc = await message_service.get_chat_messages(chat.id, reverse=True)
    
    # Verify messages are in reverse chronological order
    for i in range(len(retrieved_messages_desc) - 1):
        current_created_at = retrieved_messages_desc[i].created_at
        next_created_at = retrieved_messages_desc[i + 1].created_at
        assert current_created_at >= next_created_at
    
    # Verify content matches reverse conversation
    for i, (expected_content, expected_sender) in enumerate(reversed(conversation)):
        assert retrieved_messages_desc[i].content == expected_content
        assert retrieved_messages_desc[i].sender == expected_sender