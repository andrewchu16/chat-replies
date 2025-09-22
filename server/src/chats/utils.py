"""Utility functions for the chats module."""

from datetime import datetime
from typing import Optional


def format_chat_title(title: str) -> str:
    """
    Format and clean a chat title.
    
    Args:
        title: Raw chat title
        
    Returns:
        Formatted chat title
    """
    return title.strip()


def generate_default_chat_title() -> str:
    """
    Generate a default chat title based on current timestamp.
    
    Returns:
        Default chat title
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Chat {timestamp}"


def validate_chat_title(title: Optional[str]) -> bool:
    """
    Validate a chat title.
    
    Args:
        title: Chat title to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not title:
        return False
    
    title = title.strip()
    return 1 <= len(title) <= 255

