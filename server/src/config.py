from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource
from pydantic.fields import FieldInfo
from pydantic import Field
from typing import Any

class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == 'allowed_origins' and value is not None:
            return value.split(',')
        return value
    

class Settings(BaseSettings):
    """Global application settings."""
    
    # Database
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@postgres:5432/chat_replies_dev", description="The URL of the database to use")
    
    # Environment
    environment: str = "development"
    environment: str = Field(default="development", description="The environment to run the application in")
    debug: bool = True
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)



settings = Settings()
