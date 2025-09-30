from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .exceptions import InvalidReplyRangeError
from ..models import SenderType


class MessageReplyMetadataBase(BaseModel):
    """Base schema for message reply metadata."""

    start_index: int = Field(
        ..., ge=0, description="Start index of the reply range (inclusive)"
    )
    end_index: int = Field(
        ..., ge=0, description="End index of the reply range (exclusive)"
    )
    parent_id: str = Field(..., description="Parent message ID for reply metadata")

    def validate_range(self):
        """Validate that start_index is less than end_index."""
        if self.start_index >= self.end_index:
            raise InvalidReplyRangeError(self.start_index, self.end_index)

    def validate(self, message_content: str) -> None:
        """Validate reply metadata against original message content.

        Args:
            message_content: Original message content

        Raises:
            InvalidReplyRangeError: If reply metadata is invalid
        """
        self.validate_range()

        if self.end_index > len(message_content):
            raise InvalidReplyRangeError(self.start_index, self.end_index)

        if self.start_index < 0:
            raise InvalidReplyRangeError(self.start_index, self.end_index)


class MessageReplyMetadataCreate(MessageReplyMetadataBase):
    """Schema for creating message reply metadata."""


class MessageReplyMetadataResponse(MessageReplyMetadataBase):
    """Schema for message reply metadata response."""

    id: str = Field(..., description="Reply metadata ID")
    message_id: str = Field(..., description="Message ID for reply metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base schema for message data."""

    content: str = Field(..., min_length=1, description="Message content")
    sender: SenderType = Field(..., description="Message sender (user or ai)")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""


class MessageReply(MessageBase):
    """Schema for replying to a message with reply metadata."""

    reply_metadata: MessageReplyMetadataCreate = Field(
        None, description="Optional reply metadata for referencing specific text"
    )

class MessageReplyCreate(MessageReply):
    """Schema for creating a message reply."""


class MessageContextRepresentation(MessageBase):
    """Schema for the internal representation of a message for use in the LLM. It is intended to be the cropped content of the message constructed from the reply metadata if it exists.
    """

class MessageResponse(MessageBase):
    """Schema for message response data."""

    id: str = Field(..., description="Message ID")
    chat_id: str = Field(..., description="Chat ID")
    created_at: datetime = Field(..., description="Message creation timestamp")
    reply_metadata: Optional[MessageReplyMetadataResponse] = Field(
        default=None, description="Reply metadata for this message"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "chat_id": "550e8400-e29b-41d4-a716-446655440001",
                "content": "Hello, how can I help you?",
                "sender": SenderType.AI.value,
                "created_at": "2023-01-01T00:00:00Z",
                "reply_metadata": None,
            }
        }


class MessagesListResponse(BaseModel):
    """Schema for messages list response."""

    messages: list[MessageResponse] = Field(..., description="list of messages")

    class Config:
        json_schema_extra = {"example": {"messages": []}}


class StreamChunk(BaseModel):
    """Schema for streaming message chunks."""

    content: str = Field(..., description="Chunk of message content")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    message_id: Optional[str] = Field(
        None, description="Message ID (only available once created)"
    )

    class Config:
        json_schema_extra = {
            "example": {"content": "Hello", "is_final": False, "message_id": None}
        }
