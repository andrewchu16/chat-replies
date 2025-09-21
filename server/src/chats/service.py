from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import Chat
from ..exceptions import ChatNotFoundError, DatabaseError
from .schemas import ChatCreate, ChatUpdate


class ChatService:
    """Service class for chat operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_chat(self, chat_data: ChatCreate) -> Chat:
        """
        Create a new chat.
        
        Args:
            chat_data: Chat creation data
            
        Returns:
            Created chat object
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            chat = Chat(title=chat_data.title)
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            return chat
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create chat: {str(e)}")
    
    def get_chat(self, chat_id: str) -> Chat:
        """
        Get a chat by ID.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Chat object
            
        Raises:
            ChatNotFoundError: If chat is not found
        """
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ChatNotFoundError(chat_id)
        return chat
    
    def update_chat(self, chat_id: str, chat_data: ChatUpdate) -> Chat:
        """
        Update chat metadata.
        
        Args:
            chat_id: Chat ID
            chat_data: Chat update data
            
        Returns:
            Updated chat object
            
        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        chat = self.get_chat(chat_id)
        
        try:
            # Update only provided fields
            if chat_data.title is not None:
                chat.title = chat_data.title
            
            self.db.commit()
            self.db.refresh(chat)
            return chat
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update chat: {str(e)}")
    
    def delete_chat(self, chat_id: str) -> None:
        """
        Delete a chat.
        
        Args:
            chat_id: Chat ID
            
        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        chat = self.get_chat(chat_id)
        
        try:
            self.db.delete(chat)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete chat: {str(e)}")
    
    def list_chats(self, skip: int = 0, limit: int = 100) -> List[Chat]:
        """
        List chats with pagination.
        
        Args:
            skip: Number of chats to skip
            limit: Maximum number of chats to return
            
        Returns:
            List of chat objects
        """
        return (
            self.db.query(Chat)
            .order_by(Chat.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
