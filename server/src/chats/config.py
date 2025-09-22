"""Configuration for the chats module."""

from pydantic import BaseSettings


class ChatsConfig(BaseSettings):
    """Configuration settings for chats module."""
    
    # Chat settings
    max_title_length: int = 255
    min_title_length: int = 1
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_prefix = "CHATS_"


chats_config = ChatsConfig()

