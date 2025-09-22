from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import StreamingResponse
import json

from .schemas import MessageCreate, MessageReply, MessageResponse, MessagesListResponse
from .service import MessageService
from .dependencies import get_message_service

router = APIRouter()


async def generate_sse_stream(chat_id: str, message_data: MessageCreate, message_service: MessageService):
    """Generate SSE stream for message responses."""
    try:
        async for chunk in message_service.create_message_with_streaming_response(chat_id, message_data):
            # Format as SSE
            chunk_json = chunk.model_dump_json()
            yield f"data: {chunk_json}\n\n"
    except Exception as e:
        # Send error as SSE
        error_data = {"error": str(e), "is_final": True}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/{chat_id}/messages/stream")
async def send_message_stream(
    chat_id: str,
    message_data: MessageCreate,
    message_service: MessageService = Depends(get_message_service)
) -> StreamingResponse:
    """
    Send a message and stream the AI response using Server-Sent Events.
    
    Args:
        chat_id: Chat ID
        message_data: Message data with streaming enabled
        message_service: Message service dependency
        
    Returns:
        StreamingResponse with SSE format
    """
    return StreamingResponse(
        generate_sse_stream(chat_id, message_data, message_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    message_service: MessageService = Depends(get_message_service)
) -> MessageResponse:
    """
    Send a new message to a chat.
    
    Args:
        chat_id: Chat ID
        message_data: Message creation data
        message_service: Message service dependency
        
    Returns:
        Created message data
    """
    message = await message_service.create_message(chat_id, message_data)
    return MessageResponse.model_validate(message)


@router.post("/{chat_id}/messages/{message_id}/reply", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_message(
    chat_id: str,
    message_id: str,
    reply_data: MessageReply,
    message_service: MessageService = Depends(get_message_service)
) -> MessageResponse:
    """
    Reply to a specific message with optional reply metadata.
    
    Args:
        chat_id: Chat ID
        message_id: Message ID to reply to
        reply_data: Reply data
        message_service: Message service dependency
        
    Returns:
        Created reply message data
    """
    message = await message_service.reply_to_message(chat_id, message_id, reply_data)
    return MessageResponse.model_validate(message)


async def generate_reply_sse_stream(chat_id: str, message_id: str, reply_data: MessageReply, message_service: MessageService):
    """Generate SSE stream for reply responses."""
    try:
        async for chunk in message_service.reply_to_message_with_streaming_response(chat_id, message_id, reply_data):
            # Format as SSE
            chunk_json = chunk.model_dump_json()
            yield f"data: {chunk_json}\n\n"
    except Exception as e:
        # Send error as SSE
        error_data = {"error": str(e), "is_final": True}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/{chat_id}/messages/{message_id}/reply/stream")
async def reply_to_message_stream(
    chat_id: str,
    message_id: str,
    reply_data: MessageReply,
    message_service: MessageService = Depends(get_message_service)
) -> StreamingResponse:
    """
    Reply to a message and stream the AI response using Server-Sent Events.
    
    Args:
        chat_id: Chat ID
        message_id: Message ID to reply to
        reply_data: Reply data with streaming enabled
        message_service: Message service dependency
        
    Returns:
        StreamingResponse with SSE format
    """
    return StreamingResponse(
        generate_reply_sse_stream(chat_id, message_id, reply_data, message_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/{chat_id}/messages", response_model=MessagesListResponse)
async def get_chat_messages(
    chat_id: str,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of messages to return"),
    message_service: MessageService = Depends(get_message_service)
) -> MessagesListResponse:
    """
    Get all messages in a chat with pagination.
    
    Args:
        chat_id: Chat ID
        skip: Number of messages to skip
        limit: Maximum number of messages to return
        message_service: Message service dependency
        
    Returns:
        List of messages with pagination info
    """
    messages = await message_service.get_chat_messages(chat_id, skip, limit)
    total = await message_service.count_chat_messages(chat_id)
    
    return MessagesListResponse(
        messages=[MessageResponse.model_validate(msg) for msg in messages],
        total=total
    )


@router.get("/{chat_id}/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    chat_id: str,
    message_id: str,
    message_service: MessageService = Depends(get_message_service)
) -> MessageResponse:
    """
    Get a specific message by ID.
    
    Args:
        chat_id: Chat ID
        message_id: Message ID
        message_service: Message service dependency
        
    Returns:
        Message data
    """
    message = await message_service.get_message(chat_id, message_id)
    return MessageResponse.model_validate(message)
