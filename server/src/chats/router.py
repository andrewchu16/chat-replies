from fastapi import APIRouter, Depends, status
from typing import List

from .schemas import ChatCreate, ChatUpdate, ChatResponse
from .service import ChatService
from .dependencies import get_chat_service

router = APIRouter()


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_data: ChatCreate,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Create a new chat.
    
    Args:
        chat_data: Chat creation data
        chat_service: Chat service dependency
        
    Returns:
        Created chat data
    """
    chat = chat_service.create_chat(chat_data)
    return ChatResponse.model_validate(chat)


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Get chat metadata by ID.
    
    Args:
        chat_id: Chat ID
        chat_service: Chat service dependency
        
    Returns:
        Chat metadata
    """
    chat = chat_service.get_chat(chat_id)
    return ChatResponse.model_validate(chat)


@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: str,
    chat_data: ChatUpdate,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Update chat metadata.
    
    Args:
        chat_id: Chat ID
        chat_data: Chat update data
        chat_service: Chat service dependency
        
    Returns:
        Updated chat data
    """
    chat = chat_service.update_chat(chat_id, chat_data)
    return ChatResponse.model_validate(chat)
