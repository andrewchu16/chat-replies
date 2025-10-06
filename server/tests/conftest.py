"""Pytest configuration and fixtures."""
import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Set test database URL before importing main app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///db/memory.db"

from src.main import app
from src.database import get_db, Base
import src.database

# Use file-based SQLite for testing
SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=True,
)
TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db

# Override database configuration for testing
src.database.engine = engine
src.database.async_session = TestingSessionLocal


@pytest_asyncio.fixture
async def db():
    """Create a fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing."""
    return {"title": "Test Chat"}


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "content": "Hello, this is a test message",
        "sender": "user"
    }


@pytest.fixture
def sample_reply_data():
    """Sample reply data for testing."""
    return {
        "content": "This is a reply to the test message",
        "sender": "ai",
        "reply_metadata": {
            "start_index": 0,
            "end_index": 5
        }
    }
