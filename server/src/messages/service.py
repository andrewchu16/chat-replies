from typing import AsyncGenerator, Optional
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy import func as sa_func
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage as LCBaseMessage, HumanMessage as LCHumanMessage, AIMessage as LCAIMessage, SystemMessage as LCSystemMessage
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
            self._llm = ChatOpenAI(model="openai:gpt-5-nano")
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
    
    async def get_chat_messages(self, chat_id: str, skip: int = 0, limit: int = 100) -> list[Message]:
        """
        Get all messages in a chat with pagination.
        
        Args:
            chat_id: Chat ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return
            
        Returns:
            list of message objects
            
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
            select(sa_func.count(Message.id)).where(Message.chat_id == chat_id)
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
        await self.create_message(chat_id, user_message_data)
        
        # Build chat history context using the last 10 messages (including the new one)
        recent_messages = await self._get_last_chat_messages(chat_id, limit=10)
        messages_for_llm = self._build_chat_history_messages(
            recent_messages,
            system_preamble=(
                "You are ChatReplies assistant. Use the conversation history to respond helpfully and concisely."
            )
        )

        # Stream the AI response directly from the LLM
        message_id = str(uuid.uuid4())
        accumulated_content = ""
        try:
            async for llm_chunk in self._stream_ai_response(messages_for_llm):
                accumulated_content += llm_chunk
                yield StreamChunk(
                    content=llm_chunk,
                    is_final=False,
                    message_id=message_id
                )
        finally:
            # After streaming completes (or is interrupted), persist what we have
            try:
                if accumulated_content.strip():
                    ai_message = Message(
                        id=message_id,
                        chat_id=chat_id,
                        content=accumulated_content.strip(),
                        sender=SenderType.AI
                    )
                    self.db.add(ai_message)
                    await self.db.commit()
                    await self.db.refresh(ai_message)
                else:
                    # Ensure we don't leave open transactions
                    await self.db.rollback()
            except IntegrityError as e:
                await self.db.rollback()
                raise DatabaseError(f"Failed to create AI message: {str(e)}")

        # Send a final terminator chunk
        yield StreamChunk(
            content="",
            is_final=True,
            message_id=message_id
        )

    async def _stream_ai_response(self, messages: list[LCBaseMessage]) -> AsyncGenerator[str, None]:
        """
        Stream an AI response incrementally, yielding content chunks as they arrive.
        """
        async for chunk in self.llm.astream(messages):
            # LangChain's astream yields chunks with incremental .content
            if chunk.content:
                yield chunk.content

    async def _get_last_chat_messages(self, chat_id: str, limit: int = 10) -> list[Message]:
        """
        Fetch the most recent messages in a chat, limited by the provided count.
        Returns messages in chronological order (oldest to newest).
        """
        # Verify chat exists
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise ChatNotFoundError(chat_id)

        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages_desc = result.scalars().all()
        # Return in chronological order
        return list(reversed(messages_desc))

    def _build_chat_history_messages(
        self,
        messages: list[Message],
        *,
        system_preamble: Optional[str] = None,
        extra_system_notes: Optional[str] = None,
    ) -> list[LCBaseMessage]:
        """
        Convert persisted messages to LangChain BaseMessage list in chronological order.
        Optionally prepend a SystemMessage with guidance and notes.
        """
        chat_messages: list[LCBaseMessage] = []
        if system_preamble or extra_system_notes:
            parts: list[str] = []
            if system_preamble:
                parts.append(system_preamble)
            if extra_system_notes:
                parts.append(extra_system_notes)
            chat_messages.append(LCSystemMessage(content="\n\n".join(parts)))

        for msg in messages:
            if msg.sender == SenderType.USER:
                chat_messages.append(LCHumanMessage(content=msg.content))
            else:
                chat_messages.append(LCAIMessage(content=msg.content))
        return chat_messages
    
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

        # Build chat history context using the last 10 messages (including the new reply)
        recent_messages = await self._get_last_chat_messages(chat_id, limit=10)
        if reply_data.reply_metadata:
            referenced_text = original_message.content[
                reply_data.reply_metadata.start_index:reply_data.reply_metadata.end_index
            ]
            extra_notes = (
                f"The user replied specifically to this text: '{referenced_text}'. "
                f"Their reply content was: '{reply_data.content}'. Respond accordingly."
            )
        else:
            extra_notes = (
                f"The user replied to the previous message with: '{reply_data.content}'. Respond accordingly."
            )
        messages_for_llm = self._build_chat_history_messages(
            recent_messages,
            system_preamble=(
                "You are ChatReplies assistant. Use the conversation history to respond helpfully and concisely."
            ),
            extra_system_notes=extra_notes,
        )

        # Stream the AI response directly from the LLM
        ai_message_id = str(uuid.uuid4())
        accumulated_content = ""
        try:
            async for llm_chunk in self._stream_ai_response(messages_for_llm):
                accumulated_content += llm_chunk
                yield StreamChunk(
                    content=llm_chunk,
                    is_final=False,
                    message_id=ai_message_id
                )
        finally:
            # After streaming completes (or is interrupted), persist what we have
            try:
                if accumulated_content.strip():
                    ai_message = Message(
                        id=ai_message_id,
                        chat_id=chat_id,
                        content=accumulated_content.strip(),
                        sender=SenderType.AI
                    )
                    self.db.add(ai_message)
                    await self.db.commit()
                    await self.db.refresh(ai_message)
                else:
                    await self.db.rollback()
            except IntegrityError as e:
                await self.db.rollback()
                raise DatabaseError(f"Failed to create AI reply message: {str(e)}")

        # Send a final terminator chunk
        yield StreamChunk(
            content="",
            is_final=True,
            message_id=ai_message_id
        )
    
    async def _stream_ai_reply_response(
        self, 
        original_content: str, 
        reply_content: str, 
        reply_metadata: Optional[MessageReplyMetadataCreate]
    ) -> AsyncGenerator[str, None]:
        """
        Stream an AI response that specifically addresses the user's reply content
        in the context of the referenced original message text when provided.
        """
        system_preamble = (
            "You are ChatReplies assistant. You must reply directly and specifically to the user's "
            "reply content, taking into account the referenced portion of the original message if given. "
            "Be helpful and concise."
        )

        if reply_metadata:
            referenced_text = original_content[reply_metadata.start_index:reply_metadata.end_index]
            extra_notes = (
                f"The user replied specifically to this text: '{referenced_text}'. "
                f"Their reply content was: '{reply_content}'. Respond specifically to their reply content in this context."
            )
        else:
            extra_notes = (
                f"The user replied to the previous message with: '{reply_content}'. "
                f"Respond specifically to their reply content in the context of the conversation."
            )

        messages_for_llm = self._build_chat_history_messages(
            messages=[],
            system_preamble=system_preamble,
            extra_system_notes=extra_notes,
        )

        async for chunk in self._stream_ai_response(messages_for_llm):
            yield chunk
