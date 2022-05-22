from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.enums import ReactionTypeEnum


@dataclass
class Training:
    id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    name: str
    user_id: UUID


@dataclass
class Reaction:
    id: UUID
    reaction_type: ReactionTypeEnum
    user_id: UUID


@dataclass
class User:
    id: UUID
    email: str
