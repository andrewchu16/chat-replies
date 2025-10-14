from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .database import Base
from .utils import get_utc_now

class SenderType(str, enum.Enum):
    """Enum for message sender types."""
    USER = "user"
    AI = "ai"


class Chat(Base):
    """Chat model representing a conversation."""
    
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    # Relationships
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    """Message model representing a single message in a chat."""
    
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    content = Column(Text, nullable=False)
    sender = Column(Enum(SenderType), nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    reply_metadata = relationship("MessageReplyMetadata", back_populates="message", cascade="all, delete-orphan")


class MessageReplyMetadata(Base):
    """Message reply metadata model for tracking message replies with specific text ranges."""
    
    __tablename__ = "message_reply_metadata"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    parent_id = Column(String, nullable=False)
    start_index = Column(Integer, nullable=False)
    end_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="reply_metadata")

