"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as c:
        yield c


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
