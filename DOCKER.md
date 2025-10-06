# Docker Setup for Chat Replies

This project includes Docker configuration for both development and production environments.

## Quick Start

### Production Environment

1. Copy the environment file:
   ```bash
   cp .env.prod.example .env.prod
   ```

2. Update the `.env` file with your desired configuration.

3. Build and start all services:
   ```bash
   docker compose -f compose.prod.yaml up --build -d postgres server client
   ```

### Development Environment

1. Copy the environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Start the development environment:
   ```bash
   docker compose -f compose.dev.yaml up --build -w postgres server client
   ```

### Tests

1. Copy the environment file:
   ```bash
   cp .env.local.example .env.local
   ```

2. Start the testing environment:
   ```bash
   docker compose -f compose.dev.yaml up --build postgres server-test
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
