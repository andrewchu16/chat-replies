from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from ..models import SenderType


class MessageReplyMetadataBase(BaseModel):
    """Base schema for message reply metadata."""
    start_index: int = Field(..., ge=0, description="Start index of the reply range")
    end_index: int = Field(..., ge=0, description="End index of the reply range")
    
    def validate_range(self):
        """Validate that start_index is less than end_index."""
        if self.start_index >= self.end_index:
            raise ValueError("start_index must be less than end_index")


class MessageReplyMetadataCreate(MessageReplyMetadataBase):
    """Schema for creating message reply metadata."""
    pass


class MessageReplyMetadataResponse(MessageReplyMetadataBase):
    """Schema for message reply metadata response."""
    id: str = Field(..., description="Reply metadata ID")
    message_id: str = Field(..., description="Message ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base schema for message data."""
    content: str = Field(..., min_length=1, description="Message content")
    sender: SenderType = Field(..., description="Message sender (user or ai)")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageReply(MessageBase):
    """Schema for replying to a message with reply metadata."""
    reply_metadata: Optional[MessageReplyMetadataCreate] = Field(
        None, 
        description="Optional reply metadata for referencing specific text"
    )


class MessageResponse(MessageBase):
    """Schema for message response data."""
    id: str = Field(..., description="Message ID")
    chat_id: str = Field(..., description="Chat ID")
    created_at: datetime = Field(..., description="Message creation timestamp")
    reply_metadata: List[MessageReplyMetadataResponse] = Field(
        default_factory=list,
        description="List of reply metadata for this message"
    )
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "chat_id": "550e8400-e29b-41d4-a716-446655440001",
                "content": "Hello, how can I help you?",
                "sender": "ai",
                "created_at": "2023-01-01T00:00:00Z",
                "reply_metadata": []
            }
        }


class MessagesListResponse(BaseModel):
    """Schema for messages list response."""
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [],
                "total": 0
            }
        }
