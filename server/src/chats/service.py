from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func

from ..models import Chat
from ..exceptions import ChatNotFoundError, DatabaseError
from .schemas import ChatCreate, ChatUpdate


class ChatService:
    """Service class for chat operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_chat(self, chat_data: ChatCreate) -> Chat:
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
            await self.db.commit()
            await self.db.refresh(chat)
            return chat
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create chat: {str(e)}")
    
    async def get_chat(self, chat_id: str) -> Chat:
        """
        Get a chat by ID.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Chat object
            
        Raises:
            ChatNotFoundError: If chat is not found
        """
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise ChatNotFoundError(chat_id)
        return chat
    
    async def update_chat(self, chat_id: str, chat_data: ChatUpdate) -> Chat:
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
        chat = await self.get_chat(chat_id)
        
        try:
            # Update only provided fields
            if chat_data.title is not None:
                chat.title = chat_data.title
            
            await self.db.commit()
            await self.db.refresh(chat)
            return chat
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to update chat: {str(e)}")
    
    async def delete_chat(self, chat_id: str) -> None:
        """
        Delete a chat.
        
        Args:
            chat_id: Chat ID
            
        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        chat = await self.get_chat(chat_id)
        
        try:
            await self.db.delete(chat)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to delete chat: {str(e)}")
    
    async def list_chats(self, skip: int = 0, limit: int = 100) -> tuple[list[Chat], int]:
        """
        List chats with pagination.
        
        Args:
            skip: Number of chats to skip (ordered by created_at in descending order)
            limit: Maximum number of chats to return
            
        Returns:
            tuple of (list of chat objects, total count of chats)
        """
        # Get total count
        count_result = await self.db.execute(select(func.count(Chat.id)))
        total = count_result.scalar() or 0
        
        # Get paginated chats
        result = await self.db.execute(
            select(Chat)
            .order_by(Chat.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        chats = result.scalars().all()
        
        return list(chats), total

