import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID

from chat_api.db.db import Base


class Platform(enum.Enum):
    sherab = "sherab"
    webuddhist = "webuddhist"
    webuddhist_app = "webuddhist-app"


class Thread(Base):
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    platform = Column(Enum(Platform), nullable=False)
