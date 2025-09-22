from fastapi import HTTPException, status


class ChatTitleTooLongError(HTTPException):
    """Exception raised when chat title exceeds maximum length."""
    
    def __init__(self, max_length: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chat title cannot exceed {max_length} characters"
        )


class ChatTitleEmptyError(HTTPException):
    """Exception raised when chat title is empty."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat title cannot be empty"
        )

