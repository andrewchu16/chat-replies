from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import Message, MessageReplyMetadata, Chat
from ..exceptions import MessageNotFoundError, ChatNotFoundError, DatabaseError, InvalidReplyRangeError
from .schemas import MessageCreate, MessageReply, MessageReplyMetadataCreate


class MessageService:
    """Service class for message operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(self, chat_id: str, message_data: MessageCreate) -> Message:
        """
        Create a new message in a chat.
        
        Args:
            chat_id: Chat ID
            message_data: Message creation data
            
        Returns:
            Created message object
            
        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        # Verify chat exists
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        try:
            message = Message(
                chat_id=chat_id,
                content=message_data.content,
                sender=message_data.sender
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create message: {str(e)}")
    
    def reply_to_message(self, chat_id: str, message_id: str, reply_data: MessageReply) -> Message:
        """
        Reply to a specific message with optional reply metadata.
        
        Args:
            chat_id: Chat ID
            message_id: Message ID to reply to
            reply_data: Reply data
            
        Returns:
            Created reply message object
            
        Raises:
            ChatNotFoundError: If chat is not found
            MessageNotFoundError: If message is not found
            InvalidReplyRangeError: If reply range is invalid
            DatabaseError: If database operation fails
        """
        # Verify chat exists
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        # Verify message exists and belongs to the chat
        original_message = (
            self.db.query(Message)
            .filter(Message.id == message_id, Message.chat_id == chat_id)
            .first()
        )
        if not original_message:
            raise MessageNotFoundError(message_id)
        
        # Validate reply metadata if provided
        if reply_data.reply_metadata:
            self._validate_reply_metadata(reply_data.reply_metadata, original_message.content)
        
        try:
            # Create the reply message
            reply_message = Message(
                chat_id=chat_id,
                content=reply_data.content,
                sender=reply_data.sender
            )
            self.db.add(reply_message)
            self.db.flush()  # Flush to get the message ID
            
            # Create reply metadata if provided
            if reply_data.reply_metadata:
                reply_metadata = MessageReplyMetadata(
                    message_id=reply_message.id,
                    start_index=reply_data.reply_metadata.start_index,
                    end_index=reply_data.reply_metadata.end_index
                )
                self.db.add(reply_metadata)
            
            self.db.commit()
            self.db.refresh(reply_message)
            return reply_message
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create reply: {str(e)}")
    
    def get_message(self, chat_id: str, message_id: str) -> Message:
        """
        Get a message by ID within a specific chat.
        
        Args:
            chat_id: Chat ID
            message_id: Message ID
            
        Returns:
            Message object
            
        Raises:
            MessageNotFoundError: If message is not found
        """
        message = (
            self.db.query(Message)
            .filter(Message.id == message_id, Message.chat_id == chat_id)
            .first()
        )
        if not message:
            raise MessageNotFoundError(message_id)
        return message
    
    def get_chat_messages(self, chat_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        """
        Get all messages in a chat with pagination.
        
        Args:
            chat_id: Chat ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return
            
        Returns:
            List of message objects
            
        Raises:
            ChatNotFoundError: If chat is not found
        """
        # Verify chat exists
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        return (
            self.db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_chat_messages(self, chat_id: str) -> int:
        """
        Count total messages in a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Total number of messages
        """
        return self.db.query(Message).filter(Message.chat_id == chat_id).count()
    
    def _validate_reply_metadata(self, reply_metadata: MessageReplyMetadataCreate, original_content: str) -> None:
        """
        Validate reply metadata against original message content.
        
        Args:
            reply_metadata: Reply metadata to validate
            original_content: Original message content
            
        Raises:
            InvalidReplyRangeError: If reply range is invalid
        """
        if reply_metadata.start_index >= reply_metadata.end_index:
            raise InvalidReplyRangeError(reply_metadata.start_index, reply_metadata.end_index)
        
        if reply_metadata.end_index > len(original_content):
            raise InvalidReplyRangeError(
                reply_metadata.start_index, 
                reply_metadata.end_index
            )
        
        if reply_metadata.start_index < 0:
            raise InvalidReplyRangeError(reply_metadata.start_index, reply_metadata.end_index)
