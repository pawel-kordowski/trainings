from uuid import uuid4

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.enums import TrainingVisibilityEnum
from app.models.base import Base


class Profile(Base):
    __tablename__ = "profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, unique=True
    )
    training_visibility = Column(
        Enum(TrainingVisibilityEnum),
        default=TrainingVisibilityEnum.public,
        nullable=False,
    )

    user = relationship("User", back_populates="profile")
