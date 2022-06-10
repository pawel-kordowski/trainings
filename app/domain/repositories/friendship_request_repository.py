from uuid import UUID

from app.domain import entities
from app.domain.repositories.base import PostgresRepository


class FriendshipRequestRepository(PostgresRepository):
    async def does_pending_request_exists(
        self, sender_id: UUID, receiver_id: UUID
    ) -> bool:
        pass

    async def create_pending_request(
        self, sender_id: UUID, receiver_id: UUID
    ) -> entities.FriendshipRequest:
        pass
