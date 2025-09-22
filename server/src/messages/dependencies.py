from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .service import MessageService


def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency to get message service instance."""
    return MessageService(db)

