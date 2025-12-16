import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum

from chat_api.db.db import Base


class PlatformEnum(str, enum.Enum):
    """Platform enum for thread platform types"""
    sherab = "sherab"
    webuddhist = "webuddhist"
    webuddhist_app = "webuddhist-app"


class Thread(Base):
    """Thread model for storing chat threads"""
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    platform = Column(SQLEnum(PlatformEnum, name="platform_enum"), nullable=False)

    def __repr__(self):
        return f"<Thread(id={self.id}, email={self.email}, platform={self.platform})>"

