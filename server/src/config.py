from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource
from pydantic.fields import FieldInfo
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
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatdb"
    
    # Environment
    environment: str = "development"
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
