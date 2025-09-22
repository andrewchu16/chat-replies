from fastapi import APIRouter, Depends, status, Query

from .schemas import ChatCreate, ChatUpdate, ChatResponse
from .service import ChatService
from .dependencies import get_chat_service
from ..pagination import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ChatResponse])
async def list_chats(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    chat_service: ChatService = Depends(get_chat_service)
) -> PaginatedResponse[ChatResponse]:
    """
    List all chats with pagination.
    
    Args:
        page: Page number (1-indexed)
        size: Number of items per page (max 100)
        chat_service: Chat service dependency
        
    Returns:
        Paginated list of chats
    """
    skip = (page - 1) * size
    chats, total = await chat_service.list_chats(skip=skip, limit=size)
    
    # Calculate pagination info
    pages = (total + size - 1) // size if total > 0 else 0
    
    # Convert to response models
    chat_responses = [ChatResponse.model_validate(chat) for chat in chats]
    
    return PaginatedResponse[ChatResponse](
        items=chat_responses,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_previous=page > 1
    )


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
    chat = await chat_service.create_chat(chat_data)
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
    chat = await chat_service.get_chat(chat_id)
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
    chat = await chat_service.update_chat(chat_id, chat_data)
    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> None:
    """
    Delete a chat by ID.
    
    Args:
        chat_id: Chat ID
        chat_service: Chat service dependency
        
    Returns:
        None (204 No Content)
    """
    await chat_service.delete_chat(chat_id)
    return None
