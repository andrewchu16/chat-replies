"""Utility functions for the messages module."""

from typing import Optional
from datetime import datetime


def truncate_message_content(content: str, max_length: int = 100) -> str:
    """
    Truncate message content for display purposes.
    
    Args:
        content: Original message content
        max_length: Maximum length for truncated content
        
    Returns:
        Truncated content with ellipsis if needed
    """
    if len(content) <= max_length:
        return content
    return content[:max_length - 3] + "..."


def extract_reply_text(content: str, start_index: int, end_index: int) -> str:
    """
    Extract the text being replied to from the original message.
    
    Args:
        content: Original message content
        start_index: Start index of the reply range
        end_index: End index of the reply range
        
    Returns:
        Extracted text from the reply range
    """
    if start_index < 0 or end_index > len(content) or start_index >= end_index:
        return ""
    
    return content[start_index:end_index]


def validate_message_content(content: Optional[str]) -> bool:
    """
    Validate message content.
    
    Args:
        content: Message content to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not content:
        return False
    
    content = content.strip()
    return 1 <= len(content) <= 10000


def format_message_preview(content: str, max_length: int = 50) -> str:
    """
    Format message content for preview display.
    
    Args:
        content: Message content
        max_length: Maximum length for preview
        
    Returns:
        Formatted preview text
    """
    # Remove extra whitespace and newlines
    formatted = " ".join(content.split())
    
    # Truncate if necessary
    if len(formatted) > max_length:
        formatted = formatted[:max_length - 3] + "..."
    
    return formatted
