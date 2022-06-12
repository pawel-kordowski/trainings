from uuid import UUID

from app import enums
from app.domain import entities
from app.domain.repositories.friendship_repository import FriendshipRepository
from app.domain.repositories.friendship_request_repository import (
    FriendshipRequestRepository,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.exceptions import (
    FriendshipRequestAlreadyCreated,
    PendingFriendshipRequestDoesNotExist,
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
            does_pending_request_exist = (
                await friendship_request_repository.does_pending_request_exist(
                    user_1_id=sender_id, user_2_id=receiver_id
                )
            )
            if does_pending_request_exist:
                raise FriendshipRequestAlreadyCreated
            return await friendship_request_repository.create_pending_request(
                sender_id=sender_id, receiver_id=receiver_id
            )

    @staticmethod
    async def get_pending_requests_sent_by_user(
        user_id: UUID,
    ) -> list[entities.FriendshipRequest]:
        async with FriendshipRequestRepository() as friendship_request_repository:
            return (
                await friendship_request_repository.get_pending_requests_sent_by_user(
                    user_id=user_id
                )
            )

    @staticmethod
    async def get_pending_requests_received_by_user(
        user_id: UUID,
    ) -> list[entities.FriendshipRequest]:
        async with FriendshipRequestRepository() as friendship_request_repository:
            return await friendship_request_repository.get_pending_requests_received_by_user(  # noqa
                user_id=user_id
            )

    @classmethod
    async def accept_friendship_request(
        cls, user_id: UUID, friendship_request_id: UUID
    ):
        async with (
            FriendshipRequestRepository() as friendship_request_repository,
            FriendshipRepository() as friendship_repository,
        ):
            friendship_request = await cls._get_pending_request_received_by_user(
                friendship_request_repository=friendship_request_repository,
                friendship_request_id=friendship_request_id,
                user_id=user_id,
            )
            await friendship_request_repository.update_status(
                friendship_request_id=friendship_request_id,
                status=enums.FriendshipRequestStatusEnum.accepted,
            )
            await friendship_repository.create_friendship(
                user_1_id=friendship_request.sender_id,
                user_2_id=friendship_request.receiver_id,
            )
            await friendship_repository.create_friendship(
                user_1_id=friendship_request.receiver_id,
                user_2_id=friendship_request.sender_id,
            )

    @classmethod
    async def reject_friendship_request(
        cls, user_id: UUID, friendship_request_id: UUID
    ):
        async with FriendshipRequestRepository() as friendship_request_repository:
            await cls._get_pending_request_received_by_user(
                friendship_request_repository=friendship_request_repository,
                friendship_request_id=friendship_request_id,
                user_id=user_id,
            )
            await friendship_request_repository.update_status(
                friendship_request_id=friendship_request_id,
                status=enums.FriendshipRequestStatusEnum.rejected,
            )

    @classmethod
    async def cancel_friendship_request(
        cls, user_id: UUID, friendship_request_id: UUID
    ):
        async with FriendshipRequestRepository() as friendship_request_repository:
            await cls._get_pending_request_sent_by_user(
                friendship_request_repository=friendship_request_repository,
                friendship_request_id=friendship_request_id,
                user_id=user_id,
            )
            await friendship_request_repository.update_status(
                friendship_request_id=friendship_request_id,
                status=enums.FriendshipRequestStatusEnum.cancelled,
            )

    @classmethod
    async def _get_pending_request(
        cls,
        friendship_request_repository: FriendshipRequestRepository,
        friendship_request_id: UUID,
    ) -> entities.FriendshipRequest:
        friendship_request = await friendship_request_repository.get_request_by_id(
            friendship_request_id=friendship_request_id
        )
        if (
            not friendship_request
            or friendship_request.status != enums.FriendshipRequestStatusEnum.pending
        ):
            raise PendingFriendshipRequestDoesNotExist
        return friendship_request

    @classmethod
    async def _get_pending_request_sent_by_user(
        cls,
        friendship_request_repository: FriendshipRequestRepository,
        friendship_request_id: UUID,
        user_id: UUID,
    ) -> entities.FriendshipRequest:
        friendship_request = await cls._get_pending_request(
            friendship_request_repository=friendship_request_repository,
            friendship_request_id=friendship_request_id,
        )
        if friendship_request.sender_id != user_id:
            raise PendingFriendshipRequestDoesNotExist
        return friendship_request

    @classmethod
    async def _get_pending_request_received_by_user(
        cls,
        friendship_request_repository: FriendshipRequestRepository,
        friendship_request_id: UUID,
        user_id: UUID,
    ) -> entities.FriendshipRequest:
        friendship_request = await cls._get_pending_request(
            friendship_request_repository=friendship_request_repository,
            friendship_request_id=friendship_request_id,
        )
        if friendship_request.receiver_id != user_id:
            raise PendingFriendshipRequestDoesNotExist
        return friendship_request
