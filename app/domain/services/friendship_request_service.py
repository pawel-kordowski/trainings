from uuid import UUID

from app.domain import entities
from app.domain.repositories.friendship_repository import FriendshipRepository
from app.domain.repositories.friendship_request_repository import (
    FriendshipRequestRepository,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.exceptions import (
    FriendshipRequestAlreadyCreated,
    ReceiverDoesNotExist,
    UsersAreAlreadyFriends,
)


class FriendshipRequestService:
    @staticmethod
    async def create_friendship_request(
        sender_id: UUID, receiver_id: UUID
    ) -> entities.FriendshipRequest:
        async with (
            UserRepository() as user_repository,
            FriendshipRepository() as friendship_repository,
            FriendshipRequestRepository() as friendship_request_repository,
        ):
            does_receiver_exist = await user_repository.does_user_with_id_exist(
                user_id=receiver_id
            )
            if not does_receiver_exist:
                raise ReceiverDoesNotExist
            are_users_friends = await friendship_repository.are_users_friends(
                user_1_id=sender_id, user_2_id=receiver_id
            )
            if are_users_friends:
                raise UsersAreAlreadyFriends
            does_pending_request_exists = (
                await friendship_request_repository.does_pending_request_exists(
                    user_1_id=sender_id, user_2_id=receiver_id
                )
            )
            if does_pending_request_exists:
                raise FriendshipRequestAlreadyCreated
            return await friendship_request_repository.create_pending_request(
                sender_id=sender_id, receiver_id=receiver_id
            )
