from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .service import ChatService


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Dependency to get chat service instance."""
    return ChatService(db)

