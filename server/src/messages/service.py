from datetime import datetime
from typing import AsyncGenerator, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func as sa_func
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage as LCBaseMessage,
    HumanMessage as LCHumanMessage,
    AIMessage as LCAIMessage,
    SystemMessage as LCSystemMessage,
)
from langchain.chat_models import init_chat_model
from ..models import Message, MessageReplyMetadata, Chat, SenderType
from ..exceptions import (
    MessageNotFoundError,
    ChatNotFoundError,
    DatabaseError,
)
from .schemas import (
    MessageContextRepresentation,
    MessageCreate,
    MessageReplyCreate,
    MessageResponse,
    StreamChunk,
)


class MessageService:
    """Service class for message operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._llm: None | BaseChatModel = None
        self.system_prompt_send = """You are an AI chat assistant. You will be given the past few messages of the conversation. Use the conversation history to respond helpfully and concisely. Format responses with markdown, including headers, lists, and other formatting."""
        self.system_prompt_reply = """You are an AI chat assistant. You will be given a chain of replies that the user has made. Use the conversation history to respond helpfully and concisely. Format responses with markdown, including headers, lists, and other formatting."""

    @property
    def llm(self) -> BaseChatModel:
        if self._llm is None:
            self._llm = init_chat_model(model="openai:gpt-5-mini")
        return self._llm

    async def _get_chat(self, chat_id: str) -> Chat:
        """Get a chat by ID.

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

    async def _create_message(
        self, chat_id: str, message_data: MessageCreate
    ) -> Message:
        """
        Create a new message in a chat.

        Args:
            chat_id: Chat ID
            message_data: Message creation data

        Returns:
            Created message object in the database

        Raises:
            ChatNotFoundError: If chat is not found
            DatabaseError: If database operation fails
        """
        # Verify chat exists
        await self._get_chat(chat_id)

        try:
            message = Message(
                chat_id=chat_id,
                content=message_data.content,
                sender=message_data.sender,
            )
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            return message
        except IntegrityError as e:
            await self.db.rollback()
            raise DatabaseError(f"Failed to create message: {str(e)}")

    async def _create_message_reply(
        self, chat_id: str, message_id: str, reply_data: MessageReplyCreate
    ) -> Message:
        """
        Reply to a specific message with optional reply metadata.

        Args:
            chat_id: Chat ID
            message_id: Message ID to reply to
            reply_data: Reply data

        Returns:
            Created reply message object in the database

        Raises:
            ChatNotFoundError: If chat is not found
            MessageNotFoundError: If message is not found
            InvalidReplyRangeError: If reply range is invalid
            DatabaseError: If database operation fails
        """
        # Verify chat exists
        await self._get_chat(chat_id)

        # Verify message exists and belongs to the chat
        original_message = await self.get_message(chat_id, message_id)

        # Validate reply metadata
        reply_data.reply_metadata.validate(original_message.content)

        try:
            # Create the reply message
            reply_message = Message(
                chat_id=chat_id, content=reply_data.content, sender=reply_data.sender
            )
            self.db.add(reply_message)
            await self.db.flush()  # Flush to get the message ID

            # Create reply metadata
            reply_metadata = MessageReplyMetadata(
                message_id=reply_message.id,
                start_index=reply_data.reply_metadata.start_index,
                end_index=reply_data.reply_metadata.end_index,
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

    async def get_chat_messages(
        self, chat_id: str, skip: int = 0, limit: int = 100, reverse: bool = False
    ) -> list[MessageResponse]:
        """
        Get all messages in a chat with pagination.

        Args:
            chat_id: Chat ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return
            reverse: Whether to return messages in reverse chronological order
        Returns:
            list of message objects

        Raises:
            ChatNotFoundError: If chat is not found
        """
        # Verify chat exists
        await self._get_chat(chat_id)

        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(
                Message.created_at.desc() if reverse else Message.created_at.asc()
            )
            .options(selectinload(Message.reply_metadata))
            .offset(skip)
            .limit(limit)
        )

        messages = result.scalars().all()

        # Include optional reply metadata when present; otherwise set to None
        response_items: list[dict] = []
        for m in messages:
            reply_md = None
            if getattr(m, "reply_metadata", None):
                # relationship is a list; take the first entry if exists
                md = (
                    m.reply_metadata[0]
                    if isinstance(m.reply_metadata, list) and m.reply_metadata
                    else None
                )
                if md is not None:
                    reply_md = {
                        "id": md.id,
                        "message_id": md.message_id,
                        "start_index": md.start_index,
                        "end_index": md.end_index,
                        "created_at": md.created_at,
                    }

            response_items.append(
                {
                    "id": m.id,
                    "chat_id": m.chat_id,
                    "content": m.content,
                    "sender": m.sender,
                    "created_at": m.created_at,
                    "reply_metadata": reply_md,
                }
            )

        return response_items

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

    async def create_message_with_streaming_response(
        self, chat_id: str, user_message_data: MessageCreate
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
        await self._create_message(chat_id, user_message_data)

        # Build chat history context using the last 10 messages (including the new one)
        recent_messages = await self._get_last_chat_messages(chat_id, limit=10)
        messages_for_llm = self._build_chat_history_messages(
            recent_messages, system_prompt=self.system_prompt_send
        )
        

        # Stream the AI response directly from the LLM
        message_id = str(uuid.uuid4())
        accumulated_content = ""
        try:
            async for llm_chunk in self._stream_ai_response(messages_for_llm):
                accumulated_content += llm_chunk
                yield StreamChunk(
                    content=llm_chunk, is_final=False, message_id=message_id
                )
        finally:
            # After streaming completes (or is interrupted), persist what we have
            try:
                if accumulated_content.strip():
                    ai_message = Message(
                        id=message_id,
                        chat_id=chat_id,
                        content=accumulated_content.strip(),
                        sender=SenderType.AI,
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
        yield StreamChunk(content="", is_final=True, message_id=message_id)

    async def _stream_ai_response(
        self, messages: list[LCBaseMessage]
    ) -> AsyncGenerator[str, None]:
        """
        Stream an AI response incrementally, yielding content chunks as they arrive.
        """
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

    async def _get_last_chat_messages(
        self, chat_id: str, limit: int = 10
    ) -> list[MessageContextRepresentation]:
        """
        Fetch the most recent messages in a chat, limited by the provided count.
        Returns messages in chronological order (oldest to newest).
        """
        # Verify chat exists
        await self._get_chat(chat_id)

        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages_desc = result.scalars().all()

        return [
            MessageContextRepresentation(
                content=message.content,
                sender=message.sender,
                created_at=message.created_at,
            )
            for message in messages_desc
        ]

    def _build_chat_history_messages(
        self,
        messages: list[MessageContextRepresentation],
        *,
        system_prompt: Optional[str] = None,
        extra_system_notes: Optional[str] = None,
    ) -> list[LCBaseMessage]:
        """
        Convert persisted messages to LangChain BaseMessage list in chronological order.
        Optionally prepend a SystemMessage with guidance and notes.
        """
        chat_messages: list[LCBaseMessage] = []
        if system_prompt or extra_system_notes:
            parts: list[str] = []
            if system_prompt:
                parts.append(system_prompt)
            if extra_system_notes:
                parts.append(extra_system_notes)
            chat_messages.append(LCSystemMessage(content="\n\n".join(parts)))

        for msg in messages:
            if msg.sender == SenderType.USER:
                chat_messages.append(LCHumanMessage(content=msg.content))
            else:
                chat_messages.append(LCAIMessage(content=msg.content))
        return chat_messages

    async def _get_reply_chain(
        self, chat_id: str, message_id: str, min_length: int = 10
    ) -> list[MessageContextRepresentation]:
        """Get the chat history context for a reply.

        Args:
            chat_id: Chat ID
            message_id: Message ID to reply to

        Returns:
            List of MessageContextRepresentation objects making up the reply chain. If the reply chain is less than 10 messages, the last 10 messages will be added to the chain.
        """
        # Verify chat exists
        await self._get_chat(chat_id)

        id_to_message: dict[str, MessageResponse] = {}
        message_chain: list[MessageContextRepresentation] = []

        # Walk the reply chain by paging through reply-containing messages
        skip = 0
        current_message_id = message_id
        while current_message_id is not None:
            page: list[MessageResponse] = (
                await self.get_chat_messages(chat_id, limit=10, skip=skip, reverse=True)
            ).messages

            if not page:
                break

            for msg in page:
                id_to_message[msg.id] = msg

            if current_message_id in id_to_message:
                msg = id_to_message[current_message_id]
                # Use cropped content if reply metadata exists
                content = (
                    msg.content[
                        msg.reply_metadata.start_index : msg.reply_metadata.end_index
                    ]
                    if msg.reply_metadata
                    else msg.content
                )
                message_chain.append(
                    MessageContextRepresentation(
                        content=content,
                        sender=msg.sender,
                        created_at=msg.created_at,
                    )
                )
                # Move to parent in the chain when available
                current_message_id = (
                    msg.reply_metadata.parent_id if msg.reply_metadata else None
                )

            skip += 10

        # If the chain is short, backfill with messages strictly before the oldest in the chain
        if len(message_chain) < min_length:
            oldest_ts = (
                message_chain[-1].created_at if message_chain else datetime.now()
            )
            needed = min_length - len(message_chain)

            result = await self.db.execute(
                select(Message)
                .where(
                    Message.chat_id == chat_id,
                    Message.created_at < oldest_ts,
                )
                .order_by(Message.created_at.desc())
                .limit(needed)
            )
            backfill_msgs = result.scalars().all()

            for msg in backfill_msgs:
                message_chain.append(
                    MessageContextRepresentation(
                        content=msg.content,
                        sender=msg.sender,
                        created_at=msg.created_at,
                    )
                )

        # Return in chronological order (oldest to newest)
        return list(reversed(message_chain))

    async def reply_to_message_with_streaming_response(
        self, chat_id: str, message_id: str, reply_data: MessageReplyCreate
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
        await self._create_message_reply(chat_id, message_id, reply_data)

        # Get the original message for context
        original_message = await self.get_message(chat_id, message_id)

        message_chain = await self._get_reply_chain(chat_id, message_id, min_length=10)

        referenced_text = message_chain[-1].content

        if len(referenced_text) > 100:
            referenced_text = referenced_text[:50] + "..." + referenced_text[-50:]

        reply_text = reply_data.content

        if len(reply_text) > 100:
            reply_text = reply_text[:50] + "..." + reply_text[-50:]

        message_chain.append(
            MessageContextRepresentation(
                content=original_message.content,
                sender=original_message.sender,
                created_at=original_message.created_at,
            )
        )

        print(f"Message chain: {message_chain}")

        extra_notes = (
            f"The user replied specifically to this text: '{referenced_text}'. "
            f"Their reply content was: '{reply_text}'."
        )
        messages_for_llm = self._build_chat_history_messages(
            message_chain,
            system_prompt=self.system_prompt_reply,
            extra_system_notes=extra_notes,
        )

        # Stream the AI response directly from the LLM
        ai_message_id = str(uuid.uuid4())
        accumulated_content = ""
        try:
            async for llm_chunk in self._stream_ai_response(messages_for_llm):
                accumulated_content += llm_chunk
                yield StreamChunk(
                    content=llm_chunk, is_final=False, message_id=ai_message_id
                )
        finally:
            # After streaming completes (or is interrupted), persist what we have
            try:
                if accumulated_content.strip():
                    ai_message = Message(
                        id=ai_message_id,
                        chat_id=chat_id,
                        content=accumulated_content.strip(),
                        sender=SenderType.AI,
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
        yield StreamChunk(content="", is_final=True, message_id=ai_message_id)
