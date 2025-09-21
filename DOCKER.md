# Docker Setup for Chat Replies

This project includes Docker configuration for both development and production environments.

## Quick Start

### Production Environment

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your desired configuration.

3. Build and start all services:
   ```bash
   docker compose up --build
   ```

### Development Environment

1. Copy the environment file:
   ```bash
   cp .env.example .env.local
   ```

2. Start the development environment:
   ```bash
   docker compose -f compose.dev.yaml up --build -w
   ```

## Database Management

### Access PostgreSQL:
```bash
docker compose exec postgres psql -U postgres -d chat_replies
```

### Backup database:
```bash
docker compose exec postgres pg_dump -U postgres chat_replies > backup.sql
```

### Restore database:
```bash
docker compose exec -T postgres psql -U postgres -d chat_replies < backup.sql
```
