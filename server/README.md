# LLM Chat API

A FastAPI-based REST API for managing chats and messages in an LLM chat application.

## Features

- **Chat Management**: Create, read, and update chat metadata
- **Message Handling**: Send messages and replies with optional reply metadata
- **Reply System**: Reply to specific parts of messages with start/end indices
- **Database Integration**: SQLAlchemy ORM with support for multiple databases
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Testing**: Comprehensive test suite with pytest

## Project Structure

```
server/
├── src/
│   ├── chats/              # Chat-related functionality
│   │   ├── router.py       # API endpoints
│   │   ├── service.py      # Business logic
│   │   ├── schemas.py      # Pydantic models
│   │   ├── models.py       # Database models
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── config.py       # Module configuration
│   │   ├── constants.py    # Module constants
│   │   ├── exceptions.py   # Module exceptions
│   │   └── utils.py        # Utility functions
│   ├── messages/           # Message-related functionality
│   │   └── ... (same structure as chats)
│   ├── config.py           # Global configuration
│   ├── database.py         # Database setup
│   ├── models.py           # Global database models
│   ├── exceptions.py       # Global exceptions
│   ├── pagination.py       # Pagination utilities
│   └── main.py             # FastAPI app entry point
├── tests/                  # Test suite
├── requirements/           # Requirements files
│   ├── base.txt           # Base dependencies
│   ├── dev.txt            # Development dependencies
│   └── prod.txt           # Production dependencies
└── README.md
```

## API Endpoints

### Chats
- `POST /chats` - Create a new chat
- `GET /chats/{chat_id}` - Get chat metadata
- `PUT /chats/{chat_id}` - Update chat metadata

### Messages
- `POST /chats/{chat_id}/messages` - Send a new message
- `GET /chats/{chat_id}/messages` - Get all messages in a chat
- `GET /chats/{chat_id}/messages/{message_id}` - Get a specific message
- `POST /chats/{chat_id}/messages/{message_id}/reply` - Reply to a message

### Health
- `GET /health` - Health check endpoint

## Data Models

### Chat
- `id`: Unique identifier (UUID)
- `title`: Chat title (1-255 characters)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Message
- `id`: Unique identifier (UUID)
- `chat_id`: Reference to parent chat
- `content`: Message content (1-10000 characters)
- `sender`: Sender type ("user" or "ai")
- `created_at`: Creation timestamp

### Message Reply Metadata
- `id`: Unique identifier (UUID)
- `message_id`: Reference to message being replied to
- `start_index`: Start index of the text being referenced
- `end_index`: End index of the text being referenced
- `created_at`: Creation timestamp

## Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository and navigate to the server directory:
   ```bash
   cd server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Initialize the database:
   ```bash
   python -c "from src.database import create_tables; create_tables()"
   ```

### Running the Application

#### Development
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production
```bash
pip install -r requirements/prod.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## API Documentation

Once the server is running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- API root: http://localhost:8000/

## Configuration

The application uses environment variables for configuration. See `.env.example` for available options:

- `DATABASE_URL`: Database connection string
- `API_HOST`: Host to bind to (default: 0.0.0.0)
- `API_PORT`: Port to run on (default: 8000)
- `ENVIRONMENT`: Environment mode (development/production)
- `DEBUG`: Enable debug mode (true/false)

## Database

The application uses SQLAlchemy ORM and supports multiple databases:
- SQLite (default for development)
- PostgreSQL (recommended for production)
- MySQL/MariaDB

To change the database, update the `DATABASE_URL` in your `.env` file.

## License

This project is licensed under the MIT License.
