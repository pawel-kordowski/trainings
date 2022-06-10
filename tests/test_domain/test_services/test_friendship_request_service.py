from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app import enums, helpers
from app.domain.entities import FriendshipRequest
from app.domain.services.exceptions import (
    ReceiverDoesNotExist,
    FriendshipRequestAlreadyCreated,
    UsersAreAlreadyFriends,
)
from app.domain.services.friendship_request_service import FriendshipRequestService
from app.enums import FriendshipRequestStatusEnum


@patch("app.domain.services.friendship_request_service.UserRepository", autospec=True)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRepository", autospec=True
)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
class TestCreateFriendshipRequest:
    async def test_raises_exception_when_receiver_does_not_exist(
        self,
        mocked_friendship_request_repository,
        mocked_friendship_repository,
        mocked_user_repository,
    ):
        mocked_user_repository_instance = (
            mocked_user_repository.return_value.__aenter__.return_value
        )
        mocked_user_repository_instance.does_user_with_id_exist.return_value = False
        receiver_id = uuid4()

        with pytest.raises(ReceiverDoesNotExist):
            await FriendshipRequestService.create_friendship_request(
                sender_id=uuid4(), receiver_id=receiver_id
            )

        mocked_user_repository_instance.does_user_with_id_exist.assert_awaited_once_with(  # noqa
            user_id=receiver_id
        )

    async def test_raises_exception_when_users_are_already_friends(
        self,
        mocked_friendship_request_repository,
        mocked_friendship_repository,
        mocked_user_repository,
    ):
        mocked_user_repository_instance = (
            mocked_user_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_repository_instance = (
            mocked_friendship_repository.return_value.__aenter__.return_value
        )
        mocked_user_repository_instance.does_user_with_id_exist.return_value = True
        mocked_friendship_repository_instance.are_users_friends.return_value = True
        receiver_id = uuid4()
        sender_id = uuid4()

        with pytest.raises(UsersAreAlreadyFriends):
            await FriendshipRequestService.create_friendship_request(
                sender_id=sender_id, receiver_id=receiver_id
            )

        mocked_user_repository_instance.does_user_with_id_exist.assert_awaited_once_with(  # noqa
            user_id=receiver_id
        )
        mocked_friendship_repository_instance.are_users_friends.assert_awaited_once_with(  # noqa
            user_1_id=sender_id, user_2_id=receiver_id
        )

    async def test_raises_exception_when_pending_request_already_exist(
        self,
        mocked_friendship_request_repository,
        mocked_friendship_repository,
        mocked_user_repository,
    ):
        mocked_user_repository_instance = (
            mocked_user_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_repository_instance = (
            mocked_friendship_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_user_repository_instance.does_user_with_id_exist.return_value = True
        mocked_friendship_repository_instance.are_users_friends.return_value = False
        mocked_friendship_request_repository_instance.does_pending_request_exists.return_value = (  # noqa
            True
        )
        receiver_id = uuid4()
        sender_id = uuid4()

        with pytest.raises(FriendshipRequestAlreadyCreated):
            await FriendshipRequestService.create_friendship_request(
                sender_id=sender_id, receiver_id=receiver_id
            )

        mocked_user_repository_instance.does_user_with_id_exist.assert_awaited_once_with(  # noqa
            user_id=receiver_id
        )
        mocked_friendship_repository_instance.are_users_friends.assert_awaited_once_with(  # noqa
            user_1_id=sender_id, user_2_id=receiver_id
        )
        mocked_friendship_request_repository_instance.does_pending_request_exists.assert_awaited_once_with(  # noqa
            user_1_id=sender_id, user_2_id=receiver_id
        )

    async def test_successful(
        self,
        mocked_friendship_request_repository,
        mocked_friendship_repository,
        mocked_user_repository,
    ):
        mocked_user_repository_instance = (
            mocked_user_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_repository_instance = (
            mocked_friendship_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_user_repository_instance.does_user_with_id_exist.return_value = True
        mocked_friendship_repository_instance.are_users_friends.return_value = False
        mocked_friendship_request_repository_instance.does_pending_request_exists.return_value = (  # noqa
            False
        )
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            status=FriendshipRequestStatusEnum.pending,
            timestamp=datetime.utcnow(),
        )
        mocked_friendship_request_repository_instance.create_pending_request.return_value = (  # noqa
            friendship_request
        )
        receiver_id = uuid4()
        sender_id = uuid4()

        assert (
            await FriendshipRequestService.create_friendship_request(
                sender_id=sender_id, receiver_id=receiver_id
            )
            == friendship_request
        )

        mocked_user_repository_instance.does_user_with_id_exist.assert_awaited_once_with(  # noqa
            user_id=receiver_id
        )
        mocked_friendship_repository_instance.are_users_friends.assert_awaited_once_with(  # noqa
            user_1_id=sender_id, user_2_id=receiver_id
        )
        mocked_friendship_request_repository_instance.does_pending_request_exists.assert_awaited_once_with(  # noqa
            user_1_id=sender_id, user_2_id=receiver_id
        )
        mocked_friendship_request_repository_instance.create_pending_request.assert_awaited_once_with(  # noqa
            sender_id=sender_id, receiver_id=receiver_id
        )


@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
async def test_get_pending_requests_sent_by_user(mocked_friendship_request_repository):
    user_id = uuid4()
    friendship_request_1 = FriendshipRequest(
        id=uuid4(),
        sender_id=user_id,
        receiver_id=uuid4(),
        status=enums.FriendshipRequestStatusEnum.pending,
        timestamp=helpers.get_utc_now(),
    )
    friendship_request_2 = FriendshipRequest(
        id=uuid4(),
        sender_id=user_id,
        receiver_id=uuid4(),
        status=enums.FriendshipRequestStatusEnum.pending,
        timestamp=helpers.get_utc_now(),
    )
    friendship_requests = [friendship_request_1, friendship_request_2]
    mocked_friendship_request_repository_instance = (
        mocked_friendship_request_repository.return_value.__aenter__.return_value
    )
    mocked_friendship_request_repository_instance.get_pending_requests_sent_by_user.return_value = (  # noqa
        friendship_requests
    )

    assert (
        await FriendshipRequestService.get_pending_requests_sent_by_user(
            user_id=user_id
        )
        == friendship_requests
    )
    mocked_friendship_request_repository_instance.get_pending_requests_sent_by_user.assert_awaited_once_with(  # noqa
        user_id=user_id
    )
