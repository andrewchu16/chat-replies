from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = 1
    size: int = 20
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "size": 20
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_previous: bool
    
    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 20,
                "pages": 0,
                "has_next": False,
                "has_previous": False
            }
        }


def paginate(query: Query, page: int, size: int) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        size: Number of items per page
        
    Returns:
        PaginatedResponse object with paginated data
    """
    # Ensure page is at least 1
    page = max(1, page)
    
    # Calculate total count
    total = query.count()
    
    # Calculate pagination info
    pages = (total + size - 1) // size  # Ceiling division
    offset = (page - 1) * size
    
    # Get paginated items
    items = query.offset(offset).limit(size).all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_previous=page > 1
    )
