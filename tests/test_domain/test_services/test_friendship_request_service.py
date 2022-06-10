from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.domain.entities import FriendshipRequest
from app.domain.services.exceptions import (
    ReceiverDoesNotExist,
    FriendshipRequestAlreadyCreated,
)
from app.domain.services.friendship_request_service import FriendshipRequestService
from app.enums import FriendshipRequestStatusEnum


@patch("app.domain.services.friendship_request_service.UserRepository", autospec=True)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
class TestCreateFriendshipRequest:
    async def test_raises_exception_when_receiver_does_not_exist(
        self, mocked_friendship_request_repository, mocked_user_repository
    ):
        mocked_user_repository.does_user_with_id_exist.return_value = False
        receiver_id = uuid4()

        with pytest.raises(ReceiverDoesNotExist):
            await FriendshipRequestService.create_friendship_request(
                sender_id=uuid4(), receiver_id=receiver_id
            )

        mocked_user_repository.does_user_with_id_exist.assert_awaited_once_with(
            user_id=receiver_id
        )

    async def test_raises_exception_when_pending_request_already_exist(
        self, mocked_friendship_request_repository, mocked_user_repository
    ):
        mocked_user_repository.does_user_with_id_exist.return_value = True
        mocked_friendship_request_repository.does_pending_request_exists.return_value = (  # noqa
            True
        )
        receiver_id = uuid4()
        sender_id = uuid4()

        with pytest.raises(FriendshipRequestAlreadyCreated):
            await FriendshipRequestService.create_friendship_request(
                sender_id=sender_id, receiver_id=receiver_id
            )

        mocked_user_repository.does_user_with_id_exist.assert_awaited_once_with(
            user_id=receiver_id
        )
        mocked_friendship_request_repository.does_pending_request_exists.assert_awaited_once_with(  # noqa
            sender_id=sender_id, receiver_id=receiver_id
        )

    async def test_successful(
        self, mocked_friendship_request_repository, mocked_user_repository
    ):
        mocked_user_repository.does_user_with_id_exist.return_value = True
        mocked_friendship_request_repository.does_pending_request_exists.return_value = (  # noqa
            False
        )
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            status=FriendshipRequestStatusEnum.pending,
            timestamp=datetime.utcnow(),
        )
        mocked_friendship_request_repository.create_pending_request.return_value = (
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

        mocked_user_repository.does_user_with_id_exist.assert_awaited_once_with(
            user_id=receiver_id
        )
        mocked_friendship_request_repository.does_pending_request_exists.assert_awaited_once_with(  # noqa
            sender_id=sender_id, receiver_id=receiver_id
        )
        mocked_friendship_request_repository.create_pending_request.assert_awaited_once_with(  # noqa
            sender_id=sender_id, receiver_id=receiver_id
        )
