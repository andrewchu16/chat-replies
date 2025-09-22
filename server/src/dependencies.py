from .config import settings
from .exceptions import DevelopmentEnvironmentRequiredError

def require_development() -> None:
    if settings.environment != "development":
        raise DevelopmentEnvironmentRequiredError()