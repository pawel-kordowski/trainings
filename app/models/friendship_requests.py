from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import functions

from app.enums import FriendshipRequestStatusEnum
from app.models.base import Base


class FriendshipRequest(Base):
    __tablename__ = "friendship_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sender_id = Column(ForeignKey("user.id"), nullable=False)
    receiver_id = Column(ForeignKey("user.id"), nullable=False)
    status = Column(
        Enum(FriendshipRequestStatusEnum),
        default=FriendshipRequestStatusEnum.pending,
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), server_default=functions.now())
