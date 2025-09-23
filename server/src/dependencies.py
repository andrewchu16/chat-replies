from .config import settings
from .exceptions import DevelopmentEnvironmentRequiredError

def require_dev_environment() -> None:
    if settings.environment != "development":
        raise DevelopmentEnvironmentRequiredError()