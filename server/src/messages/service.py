from typing import List, AsyncGenerator, Optional
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from ..models import Message, MessageReplyMetadata, Chat, SenderType
from ..exceptions import MessageNotFoundError, ChatNotFoundError, DatabaseError, InvalidReplyRangeError
from .schemas import MessageCreate, MessageReply, MessageReplyMetadataCreate, StreamChunk


class MessageService:
    """Service class for message operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._llm: None | BaseChatModel = None
        
    @property
    def llm(self) -> BaseChatModel:
        if self._llm is None:
            self._llm = ChatOpenAI(model="openai:gpt-4o-mini")
        return self._llm
    
    async def create_message(self, chat_id: str, message_data: MessageCreate) -> Message:
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
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        try:
            message = Message(
                chat_id=chat_id,
                content=message_data.content,
                sender=message_data.sender
            )
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            return message
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create message: {str(e)}")
    
    async def reply_to_message(self, chat_id: str, message_id: str, reply_data: MessageReply) -> Message:
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
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        # Verify message exists and belongs to the chat
        result = await self.db.execute(
            select(Message).where(Message.id == message_id, Message.chat_id == chat_id)
        )
        original_message = result.scalar_one_or_none()
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
            await self.db.flush()  # Flush to get the message ID
            
            # Create reply metadata if provided
            if reply_data.reply_metadata:
                reply_metadata = MessageReplyMetadata(
                    message_id=reply_message.id,
                    start_index=reply_data.reply_metadata.start_index,
                    end_index=reply_data.reply_metadata.end_index
                )
                self.db.add(reply_metadata)
            
            await self.db.commit()
            await self.db.refresh(reply_message)
            return reply_message
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create reply: {str(e)}")
    
    async def get_message(self, chat_id: str, message_id: str) -> Message:
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
        result = await self.db.execute(
            select(Message).where(Message.id == message_id, Message.chat_id == chat_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            raise MessageNotFoundError(message_id)
        return message
    
    async def get_chat_messages(self, chat_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
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
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise ChatNotFoundError(chat_id)
        
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def count_chat_messages(self, chat_id: str) -> int:
        """
        Count total messages in a chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Total number of messages
        """
        result = await self.db.execute(
            select(func.count(Message.id)).where(Message.chat_id == chat_id)
        )
        return result.scalar()
    
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
    
    async def create_message_with_streaming_response(
        self, 
        chat_id: str, 
        user_message_data: MessageCreate
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Create a user message and stream an AI response.
        
        Args:
            chat_id: Chat ID
            user_message_data: User message data
            
        Yields:
            StreamChunk objects containing the AI response
            
        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        # First, create the user message
        user_message = await self.create_message(chat_id, user_message_data)
        
        # Generate AI response content (simulate streaming)
        ai_response_content = await self._generate_ai_response(user_message.content)
        
        # Stream the AI response
        message_id = str(uuid.uuid4())
        accumulated_content = ""
        
        # Split the response into chunks for streaming
        words = ai_response_content.split()
        chunk_size = 3  # Stream 3 words at a time
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " ".join(chunk_words)
            accumulated_content += chunk_content + " "
            
            is_final = i + chunk_size >= len(words)
            
            yield StreamChunk(
                content=chunk_content,
                is_final=is_final,
                message_id=message_id
            )
            
            # Simulate processing delay
            await asyncio.sleep(0.1)
        
        # Create the AI message in the database
        try:
            ai_message = Message(
                id=message_id,
                chat_id=chat_id,
                content=ai_response_content.strip(),
                sender=SenderType.AI
            )
            self.db.add(ai_message)
            await self.db.commit()
            await self.db.refresh(ai_message)
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create AI message: {str(e)}")
    
    async def _generate_ai_response(self, user_content: str) -> str:
        """
        Generate an AI response to user content.
        This is a placeholder implementation that simulates AI response generation.
        
        Args:
            user_content: The user's message content
            
        Returns:
            Generated AI response
        """
        # Simulate AI processing time
        await asyncio.sleep(0.5)
        
        print(f"User content: {user_content[:50]}...")
        
        # Simple response generation (replace with actual AI service)
        responses = [
            f"I understand you said: '{user_content}'. Let me help you with that.",
            f"That's an interesting question about '{user_content}'. Here's what I think...",
            f"Thanks for sharing '{user_content}'. I'd be happy to discuss this further.",
            f"Regarding '{user_content}', I have some thoughts that might be helpful.",
            f"I see you're asking about '{user_content}'. Let me provide some insights."
        ]
        
        # Simple hash-based selection for consistent responses
        response_index = hash(user_content) % len(responses)
        return responses[response_index]
    
    async def reply_to_message_with_streaming_response(
        self, 
        chat_id: str, 
        message_id: str, 
        reply_data: MessageReply
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Reply to a message and stream an AI response.
        
        Args:
            chat_id: Chat ID
            message_id: Message ID to reply to
            reply_data: Reply data
            
        Yields:
            StreamChunk objects containing the AI response
            
        Raises:
            ChatNotFoundError: If chat is not found
            MessageNotFoundError: If message is not found
            InvalidReplyRangeError: If reply range is invalid
            DatabaseError: If database operation fails
        """
        # First, create the user reply message
        await self.reply_to_message(chat_id, message_id, reply_data)
        
        # Get the original message for context
        original_message = await self.get_message(chat_id, message_id)
        
        # Generate AI response content based on the reply context
        ai_response_content = await self._generate_ai_reply_response(
            original_message.content, 
            reply_data.content,
            reply_data.reply_metadata
        )
        
        # Stream the AI response
        ai_message_id = str(uuid.uuid4())
        
        # Split the response into chunks for streaming
        words = ai_response_content.split()
        chunk_size = 3  # Stream 3 words at a time
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_content = " ".join(chunk_words)
            
            is_final = i + chunk_size >= len(words)
            
            yield StreamChunk(
                content=chunk_content,
                is_final=is_final,
                message_id=ai_message_id
            )
            
            # Simulate processing delay
            await asyncio.sleep(0.1)
        
        # Create the AI message in the database
        try:
            ai_message = Message(
                id=ai_message_id,
                chat_id=chat_id,
                content=ai_response_content.strip(),
                sender=SenderType.AI
            )
            self.db.add(ai_message)
            await self.db.commit()
            await self.db.refresh(ai_message)
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create AI reply message: {str(e)}")
    
    async def _generate_ai_reply_response(
        self, 
        original_content: str, 
        reply_content: str, 
        reply_metadata: Optional[MessageReplyMetadataCreate]
    ) -> str:
        """
        Generate an AI response to a reply message.
        This is a placeholder implementation that simulates AI response generation.
        
        Args:
            original_content: The original message content
            reply_content: The user's reply content
            reply_metadata: Optional reply metadata
            
        Returns:
            Generated AI response
        """
        # Simulate AI processing time
        await asyncio.sleep(0.5)
        
        # Create context-aware responses
        if reply_metadata:
            # Extract the specific text being replied to
            referenced_text = original_content[reply_metadata.start_index:reply_metadata.end_index]
            responses = [
                f"I see you're responding to '{referenced_text}' with '{reply_content}'. That's an interesting perspective.",
                f"Regarding your reply '{reply_content}' to '{referenced_text}', I think you make a good point.",
                f"Your response '{reply_content}' to the part about '{referenced_text}' raises some important questions.",
                f"I understand your reply '{reply_content}' to '{referenced_text}'. Let me add some thoughts...",
                f"Good point about '{referenced_text}'. Your reply '{reply_content}' makes me think of..."
            ]
        else:
            responses = [
                f"I see you replied '{reply_content}' to the message about '{original_content[:50]}...'. That's insightful.",
                f"Your reply '{reply_content}' to the previous message shows good understanding.",
                f"Thanks for your response '{reply_content}'. Building on that idea...",
                f"I appreciate your reply '{reply_content}'. This reminds me of...",
                f"Your response '{reply_content}' adds valuable context to our discussion."
            ]
        
        # Simple hash-based selection for consistent responses
        response_index = hash(reply_content + original_content) % len(responses)
        return responses[response_index]
