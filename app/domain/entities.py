from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app import models
from app.enums import FriendshipRequestStatusEnum, ReactionTypeEnum


@dataclass
class Training:
    id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    name: str
    user_id: UUID

    @classmethod
    def from_model(cls, model_instance: models.Training):
        return cls(
            id=model_instance.id,
            start_time=model_instance.start_time,
            end_time=model_instance.end_time,
            name=model_instance.name,
            user_id=model_instance.user_id,
        )


@dataclass
class Reaction:
    id: UUID
    reaction_type: ReactionTypeEnum
    user_id: UUID

    @classmethod
    def from_model(cls, model_instance: models.Reaction):
        return cls(
            id=model_instance.id,
            reaction_type=model_instance.reaction_type,
            user_id=model_instance.user_id,
        )


@dataclass
class User:
    id: UUID
    email: str

    @classmethod
    def from_model(cls, model_instance: models.User):
        return cls(id=model_instance.id, email=model_instance.email)


@dataclass
class UserWithHashedPassword(User):
    hashed_password: str = None

    @classmethod
    def from_model(cls, model_instance: models.User):
        return cls(
            id=model_instance.id,
            email=model_instance.email,
            hashed_password=model_instance.hashed_password,
        )


@dataclass
class FriendshipRequest:
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    timestamp: datetime
    status: FriendshipRequestStatusEnum
