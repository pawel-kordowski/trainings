from datetime import datetime
from uuid import UUID

import strawberry

from app.domain import entities
from app.graphql.types import User


@strawberry.type
class FriendshipRequest:
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    timestamp: datetime

    @strawberry.field
    async def sender(self) -> User:
        from app.graphql.data_loaders.users import get_users_by_ids_loader

        return await get_users_by_ids_loader.load(self.sender_id)

    @strawberry.field
    async def receiver(self) -> User:
        from app.graphql.data_loaders.users import get_users_by_ids_loader

        return await get_users_by_ids_loader.load(self.receiver_id)

    @classmethod
    def from_entity(cls, friendship_request: entities.FriendshipRequest):
        return cls(
            id=friendship_request.id,
            sender_id=friendship_request.sender_id,
            receiver_id=friendship_request.receiver_id,
            timestamp=friendship_request.timestamp,
        )
