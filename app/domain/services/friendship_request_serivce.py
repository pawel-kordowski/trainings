from uuid import UUID

from app.domain import entities


class FriendshipRequestService:
    @staticmethod
    async def create_friendship_request(
        sender_id: UUID, receiver_id: UUID
    ) -> entities.FriendshipRequest:
        pass
