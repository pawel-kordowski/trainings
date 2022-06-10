from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.enums import FriendshipRequestStatusEnum
from app.helpers import get_utc_now
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
    timestamp = Column(DateTime(timezone=True), default=get_utc_now)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
