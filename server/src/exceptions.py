from fastapi import HTTPException, status


class ChatNotFoundError(HTTPException):
    """Exception raised when a chat is not found."""
    
    def __init__(self, chat_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id '{chat_id}' not found"
        )


class MessageNotFoundError(HTTPException):
    """Exception raised when a message is not found."""
    
    def __init__(self, message_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with id '{message_id}' not found"
        )


class InvalidReplyRangeError(HTTPException):
    """Exception raised when reply range is invalid."""
    
    def __init__(self, start_index: int, end_index: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reply range: start_index ({start_index}) must be less than end_index ({end_index})"
        )


class DatabaseError(HTTPException):
    """Exception raised for database-related errors."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
