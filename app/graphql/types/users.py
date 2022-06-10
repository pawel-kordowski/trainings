from __future__ import annotations

from uuid import UUID

import strawberry

from app.domain import entities


@strawberry.type
class User:
    id: UUID
    email: str

    @classmethod
    def from_entity(cls, user: entities.User) -> User:
        return cls(id=user.id, email=user.email)


@strawberry.type
class JWT:
    jwt: str
