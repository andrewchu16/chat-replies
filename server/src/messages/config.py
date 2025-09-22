"""Configuration for the messages module."""

from pydantic import BaseSettings


class MessagesConfig(BaseSettings):
    """Configuration settings for messages module."""
    
    # Message settings
    max_content_length: int = 10000
    min_content_length: int = 1
    default_page_size: int = 100
    max_page_size: int = 1000
    
    # Reply metadata settings
    max_reply_range_length: int = 1000
    
    class Config:
        env_prefix = "MESSAGES_"


messages_config = MessagesConfig()

