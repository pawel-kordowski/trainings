from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Friendship(Base):
    __tablename__ = "friendship"

    user_1_id = Column(ForeignKey("user.id"), primary_key=True)
    user_2_id = Column(ForeignKey("user.id"), primary_key=True)

    user_1 = relationship("User", foreign_keys=[user_1_id])
    user_2 = relationship("User", foreign_keys=[user_2_id])
