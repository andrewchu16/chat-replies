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


class DatabaseError(HTTPException):
    """Exception raised for database-related errors."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DevelopmentEnvironmentRequiredError(HTTPException):
    """Exception raised when development environment is required."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Development environment is required"
        )
