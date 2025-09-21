from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .service import ChatService


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Dependency to get chat service instance."""
    return ChatService(db)
