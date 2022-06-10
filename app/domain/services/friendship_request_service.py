from uuid import UUID

from app.domain import entities
from app.domain.repositories.friendship_request_repository import (
    FriendshipRequestRepository,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.exceptions import (
    FriendshipRequestAlreadyCreated,
    ReceiverDoesNotExist,
)


class FriendshipRequestService:
    @staticmethod
    async def create_friendship_request(
        sender_id: UUID, receiver_id: UUID
    ) -> entities.FriendshipRequest:
        if not await UserRepository.does_user_with_id_exist(user_id=receiver_id):
            raise ReceiverDoesNotExist
        if await FriendshipRequestRepository.does_pending_request_exists(
            sender_id=sender_id, receiver_id=receiver_id
        ):
            raise FriendshipRequestAlreadyCreated
        return await FriendshipRequestRepository.create_pending_request(
            sender_id=sender_id, receiver_id=receiver_id
        )
