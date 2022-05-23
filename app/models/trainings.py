from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Training(Base):
    __tablename__ = "training"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    name = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    user = relationship("User", back_populates="trainings")
    reactions = relationship(
        "Reaction", back_populates="training", cascade="all, delete-orphan"
    )
