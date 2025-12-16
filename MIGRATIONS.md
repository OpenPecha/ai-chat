# Database Migrations Guide

## Overview

This project uses Alembic for managing database schema migrations with PostgreSQL.

## Setup

1. **Install dependencies** (including psycopg2-binary for Alembic):
   ```bash
   poetry install
   ```

2. **Configure database connection** in `alembic.ini`:
   ```ini
   sqlalchemy.url = postgresql://admin:chatAdmin@localhost:5434/ai_chat
   ```

## Common Commands

### Apply Migrations

Apply all pending migrations:
```bash
poetry run alembic upgrade head
```

Apply migrations up to a specific revision:
```bash
poetry run alembic upgrade <revision_id>
```

### Create New Migrations

After modifying models in `chat_api/db/models.py`:

**Auto-generate migration** (recommended):
```bash
poetry run alembic revision --autogenerate -m "description_of_changes"
```

**Create empty migration** (for custom SQL):
```bash
poetry run alembic revision -m "description_of_changes"
```

### View Migration Status

Show current revision:
```bash
poetry run alembic current
```

Show migration history:
```bash
poetry run alembic history
```

Show migration history with verbose output:
```bash
poetry run alembic history --verbose
```

### Rollback Migrations

Rollback one migration:
```bash
poetry run alembic downgrade -1
```

Rollback to a specific revision:
```bash
poetry run alembic downgrade <revision_id>
```

Rollback all migrations:
```bash
poetry run alembic downgrade base
```

## Current Models

### Thread Model

Located in `chat_api/db/models.py`

**Fields:**
- `id` (UUID): Primary key, auto-generated
- `email` (String): User email address
- `created_at` (DateTime): Timestamp of creation (auto-set)
- `updated_at` (DateTime): Timestamp of last update (auto-updated)
- `is_deleted` (Boolean): Soft delete flag (default: False)
- `platform` (Enum): Platform type - sherab, webuddhist, or webuddhist-app

**Indexes:**
- `ix_threads_email`: Index on email field for faster lookups
- `ix_threads_created_at`: Index on created_at for sorting

**Migration:** `001_create_threads_table.py`

## Project Structure

```
ai-chat/
├── alembic.ini                    # Alembic configuration
├── migrations/
│   ├── env.py                     # Alembic environment setup
│   ├── script.py.mako             # Migration template
│   └── versions/                  # Migration files
│       └── 001_create_threads_table.py
├── chat_api/
│   └── db/
│       ├── db.py                  # Database connection & Base
│       └── models.py              # SQLAlchemy models
```

## Tips

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** on a development database first
3. **Use meaningful migration messages** to describe changes
4. **Create indexes** for frequently queried columns
5. **Use soft deletes** (is_deleted flag) instead of hard deletes when possible
6. **Keep migrations small** and focused on one logical change

## Troubleshooting

### Migration fails with "relation already exists"

If you need to start fresh:
```bash
# Drop all tables
poetry run alembic downgrade base

# Re-apply migrations
poetry run alembic upgrade head
```

### Can't connect to database

Check your database is running:
```bash
docker-compose -f local_setup/docker-compose.yml ps
```

Start the database if needed:
```bash
docker-compose -f local_setup/docker-compose.yml up -d
```

### Alembic can't import models

Make sure you're importing all models in `migrations/env.py`:
```python
from chat_api.db.models import Thread  # Add all models here
```

