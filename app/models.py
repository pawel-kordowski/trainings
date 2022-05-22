from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeMeta, declarative_base, relationship

from app.enums import ReactionTypeEnum

Base: DeclarativeMeta = declarative_base()


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


class Friendship(Base):
    __tablename__ = "friendship"

    user_1_id = Column(ForeignKey("user.id"), primary_key=True)
    user_2_id = Column(ForeignKey("user.id"), primary_key=True)

    user_1 = relationship("User", foreign_keys=[user_1_id])
    user_2 = relationship("User", foreign_keys=[user_2_id])


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


class Reaction(Base):
    __tablename__ = "reaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    training_id = Column(UUID(as_uuid=True), ForeignKey("training.id"), nullable=False)
    reaction_type = Column(Enum(ReactionTypeEnum), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="reactions")
    training = relationship("Training", back_populates="reactions")
