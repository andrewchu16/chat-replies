from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class ChatBase(BaseModel):
    """Base schema for chat data."""
    title: str = Field(..., min_length=1, max_length=255, description="Chat title")


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""
    pass


class ChatUpdate(BaseModel):
    """Schema for updating chat metadata."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Chat title")


class ChatResponse(ChatBase):
    """Schema for chat response data."""
    id: str = Field(..., description="Chat ID")
    created_at: datetime = Field(..., description="Chat creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Chat last update timestamp")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "My Chat",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
