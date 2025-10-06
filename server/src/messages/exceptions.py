from fastapi import HTTPException, status


class MessageTooLongError(HTTPException):
    """Exception raised when message content exceeds maximum length."""
    
    def __init__(self, max_length: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message content cannot exceed {max_length} characters"
        )


class MessageEmptyError(HTTPException):
    """Exception raised when message content is empty."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )


class InvalidSenderTypeError(HTTPException):
    """Exception raised when sender type is invalid."""
    
    def __init__(self, sender_type: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sender type: {sender_type}. Must be 'user' or 'ai'"
        )


class ReplyMetadataOutOfBoundsError(HTTPException):
    """Exception raised when reply metadata indices are out of bounds."""
    
    def __init__(self, start_index: int, end_index: int, content_length: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reply range ({start_index}-{end_index}) is out of bounds for content length {content_length}"
        )


class InvalidReplyRangeError(HTTPException):
    """Exception raised when reply range is invalid."""
    
    def __init__(self, start_index: int, end_index: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reply range: {start_index}-{end_index}"
        )