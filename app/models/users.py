from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    trainings = relationship(
        "Training", back_populates="user", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "Reaction", back_populates="user", cascade="all, delete-orphan"
    )
