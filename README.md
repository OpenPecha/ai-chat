# ai-chat

FastAPI + Postgres + SQLAlchemy scaffold using Poetry and Docker Compose.

## Database Models

### Threads Model

The `Thread` model represents chat threads with the following fields:

- `id`: UUID (primary key, auto-generated)
- `email`: String (user email)
- `created_at`: DateTime (automatically set on creation)
- `updated_at`: DateTime (automatically updated on modification)
- `is_deleted`: Boolean (soft delete flag, defaults to False)
- `platform`: Enum (sherab, webuddhist, webuddhist-app)

## Database Migrations

This project uses Alembic for database migrations.

### Running Migrations

To apply all pending migrations to your database:

```bash
poetry run alembic upgrade head
```

### Creating New Migrations

After modifying models in `chat_api/db/models.py`, generate a new migration:

```bash
poetry run alembic revision --autogenerate -m "description_of_changes"
```

### Viewing Migration History

```bash
poetry run alembic history
```

### Rolling Back Migrations

To rollback the last migration:

```bash
poetry run alembic downgrade -1
```

To rollback to a specific revision:

```bash
poetry run alembic downgrade <revision_id>
```

## Usage Example

```python
from chat_api.db import SessionLocal, Thread, PlatformEnum
import uuid

# Create a new thread
with SessionLocal() as session:
    new_thread = Thread(
        id=uuid.uuid4(),
        email="user@example.com",
        platform=PlatformEnum.sherab
    )
    session.add(new_thread)
    session.commit()
    
    # Query threads
    threads = session.query(Thread).filter(Thread.is_deleted == False).all()
```