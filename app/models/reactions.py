from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.enums import ReactionTypeEnum
from app.models.base import Base


class Reaction(Base):
    __tablename__ = "reaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    training_id = Column(UUID(as_uuid=True), ForeignKey("training.id"), nullable=False)
    reaction_type = Column(Enum(ReactionTypeEnum), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="reactions")
    training = relationship("Training", back_populates="reactions")
