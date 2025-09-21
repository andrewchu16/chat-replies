from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .service import MessageService


def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    """Dependency to get message service instance."""
    return MessageService(db)
