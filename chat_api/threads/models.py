import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import foreign, relationship

from chat_api.db.db import Base


class DeviceType(enum.Enum):
    web = "web"
    mobile_app = "mobile_app"    

class Thread(Base):
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))
    application = relationship("Application", back_populates="threads")

    chats = relationship("Chat", back_populates="thread")
