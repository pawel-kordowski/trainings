from datetime import datetime
from unittest.mock import patch, call
from uuid import uuid4

import pytest

from app import enums, helpers
from app.domain.entities import FriendshipRequest
from app.domain.services.exceptions import (
    ReceiverDoesNotExist,
    FriendshipRequestAlreadyCreated,
    UsersAreAlreadyFriends,
    PendingFriendshipRequestForUserDoesNotExist,
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
        mocked_friendship_request_repository_instance.does_pending_request_exist.return_value = (  # noqa
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
        mocked_friendship_request_repository_instance.does_pending_request_exist.assert_awaited_once_with(  # noqa
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
        mocked_friendship_request_repository_instance.does_pending_request_exist.return_value = (  # noqa
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
        mocked_friendship_request_repository_instance.does_pending_request_exist.assert_awaited_once_with(  # noqa
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


@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
async def test_get_pending_requests_received_by_user(
    mocked_friendship_request_repository,
):
    user_id = uuid4()
    friendship_request_1 = FriendshipRequest(
        id=uuid4(),
        sender_id=uuid4(),
        receiver_id=user_id,
        status=enums.FriendshipRequestStatusEnum.pending,
        timestamp=helpers.get_utc_now(),
    )
    friendship_request_2 = FriendshipRequest(
        id=uuid4(),
        sender_id=uuid4(),
        receiver_id=user_id,
        status=enums.FriendshipRequestStatusEnum.pending,
        timestamp=helpers.get_utc_now(),
    )
    friendship_requests = [friendship_request_1, friendship_request_2]
    mocked_friendship_request_repository_instance = (
        mocked_friendship_request_repository.return_value.__aenter__.return_value
    )
    mocked_friendship_request_repository_instance.get_pending_requests_received_by_user.return_value = (  # noqa
        friendship_requests
    )

    assert (
        await FriendshipRequestService.get_pending_requests_received_by_user(
            user_id=user_id
        )
        == friendship_requests
    )
    mocked_friendship_request_repository_instance.get_pending_requests_received_by_user.assert_awaited_once_with(  # noqa
        user_id=user_id
    )


@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
class TestGetPendingRequestReceivedByUser:
    receiver_id = uuid4()

    @pytest.mark.parametrize(
        "friendship_request",
        (
            None,
            FriendshipRequest(
                id=uuid4(),
                sender_id=uuid4(),
                receiver_id=uuid4(),
                status=enums.FriendshipRequestStatusEnum.pending,
                timestamp=helpers.get_utc_now(),
            ),
            FriendshipRequest(
                id=uuid4(),
                sender_id=uuid4(),
                receiver_id=receiver_id,
                status=enums.FriendshipRequestStatusEnum.accepted,
                timestamp=helpers.get_utc_now(),
            ),
            FriendshipRequest(
                id=uuid4(),
                sender_id=uuid4(),
                receiver_id=receiver_id,
                status=enums.FriendshipRequestStatusEnum.rejected,
                timestamp=helpers.get_utc_now(),
            ),
            FriendshipRequest(
                id=uuid4(),
                sender_id=uuid4(),
                receiver_id=receiver_id,
                status=enums.FriendshipRequestStatusEnum.cancelled,
                timestamp=helpers.get_utc_now(),
            ),
        ),
    )
    async def test_raises_exception_when_request_not_found(
        self, mocked_friendship_request_repository, friendship_request
    ):
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_request_repository_instance.get_request_by_id.return_value = (
            friendship_request
        )
        friendship_request_id = uuid4()

        with pytest.raises(PendingFriendshipRequestForUserDoesNotExist):
            await FriendshipRequestService._get_pending_request_received_by_user(
                friendship_request_repository=mocked_friendship_request_repository_instance,  # noqa
                user_id=self.receiver_id,
                friendship_request_id=friendship_request_id,
            )
        mocked_friendship_request_repository_instance.get_request_by_id.assert_awaited_once_with(  # noqa
            friendship_request_id=friendship_request_id
        )

    async def test_successful(self, mocked_friendship_request_repository):
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=self.receiver_id,
            status=enums.FriendshipRequestStatusEnum.pending,
            timestamp=helpers.get_utc_now(),
        )
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_friendship_request_repository_instance.get_request_by_id.return_value = (
            friendship_request
        )

        assert (
            await FriendshipRequestService._get_pending_request_received_by_user(
                friendship_request_repository=mocked_friendship_request_repository_instance,  # noqa
                user_id=self.receiver_id,
                friendship_request_id=friendship_request.id,
            )
            == friendship_request
        )
        mocked_friendship_request_repository_instance.get_request_by_id.assert_awaited_once_with(  # noqa
            friendship_request_id=friendship_request.id
        )


@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRepository", autospec=True
)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestService"
    "._get_pending_request_received_by_user",
    autospec=True,
)
class TestAcceptFriendshipRequest:
    async def test_successful(
        self,
        mocked_get_pending_request_received_by_user,
        mocked_friendship_repository,
        mocked_friendship_request_repository,
    ):
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            status=enums.FriendshipRequestStatusEnum.pending,
            timestamp=helpers.get_utc_now(),
        )
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_get_pending_request_received_by_user.return_value = friendship_request
        mocked_friendship_repository_instance = (
            mocked_friendship_repository.return_value.__aenter__.return_value
        )

        await FriendshipRequestService.accept_friendship_request(
            user_id=friendship_request.receiver_id,
            friendship_request_id=friendship_request.id,
        )

        mocked_get_pending_request_received_by_user.assert_awaited_once_with(
            friendship_request_repository=mocked_friendship_request_repository_instance,
            friendship_request_id=friendship_request.id,
            user_id=friendship_request.receiver_id,
        )
        mocked_friendship_request_repository_instance.update_status.assert_awaited_once_with(  # noqa
            friendship_request_id=friendship_request.id,
            status=enums.FriendshipRequestStatusEnum.accepted,
        )
        mocked_friendship_repository_instance.create_friendship.assert_has_awaits(
            [
                call(
                    user_1_id=friendship_request.sender_id,
                    user_2_id=friendship_request.receiver_id,
                ),
                call(
                    user_1_id=friendship_request.receiver_id,
                    user_2_id=friendship_request.sender_id,
                ),
            ]
        )

    async def test_failure(
        self,
        mocked_get_pending_request_received_by_user,
        mocked_friendship_repository,
        mocked_friendship_request_repository,
    ):
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_get_pending_request_received_by_user.side_effect = (
            PendingFriendshipRequestForUserDoesNotExist
        )
        mocked_friendship_repository_instance = (
            mocked_friendship_repository.return_value.__aenter__.return_value
        )
        user_id = uuid4()
        friendship_request_id = uuid4()

        with pytest.raises(PendingFriendshipRequestForUserDoesNotExist):
            await FriendshipRequestService.accept_friendship_request(
                user_id=user_id, friendship_request_id=friendship_request_id
            )

        mocked_get_pending_request_received_by_user.assert_awaited_once_with(
            friendship_request_repository=mocked_friendship_request_repository_instance,
            friendship_request_id=friendship_request_id,
            user_id=user_id,
        )
        mocked_friendship_request_repository_instance.update_status.assert_not_awaited()
        mocked_friendship_repository_instance.create_friendship.assert_not_awaited()


@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestRepository",
    autospec=True,
)
@patch(
    "app.domain.services.friendship_request_service.FriendshipRequestService"
    "._get_pending_request_received_by_user",
    autospec=True,
)
class TestRejectFriendshipRequest:
    async def test_successful(
        self,
        mocked_get_pending_request_received_by_user,
        mocked_friendship_request_repository,
    ):
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=uuid4(),
            receiver_id=uuid4(),
            status=enums.FriendshipRequestStatusEnum.pending,
            timestamp=helpers.get_utc_now(),
        )
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_get_pending_request_received_by_user.return_value = friendship_request

        await FriendshipRequestService.reject_friendship_request(
            user_id=friendship_request.receiver_id,
            friendship_request_id=friendship_request.id,
        )

        mocked_get_pending_request_received_by_user.assert_awaited_once_with(
            friendship_request_repository=mocked_friendship_request_repository_instance,
            friendship_request_id=friendship_request.id,
            user_id=friendship_request.receiver_id,
        )
        mocked_friendship_request_repository_instance.update_status.assert_awaited_once_with(  # noqa
            friendship_request_id=friendship_request.id,
            status=enums.FriendshipRequestStatusEnum.rejected,
        )

    async def test_failure(
        self,
        mocked_get_pending_request_received_by_user,
        mocked_friendship_request_repository,
    ):
        mocked_friendship_request_repository_instance = (
            mocked_friendship_request_repository.return_value.__aenter__.return_value
        )
        mocked_get_pending_request_received_by_user.side_effect = (
            PendingFriendshipRequestForUserDoesNotExist
        )
        user_id = uuid4()
        friendship_request_id = uuid4()

        with pytest.raises(PendingFriendshipRequestForUserDoesNotExist):
            await FriendshipRequestService.reject_friendship_request(
                user_id=user_id, friendship_request_id=friendship_request_id
            )

        mocked_get_pending_request_received_by_user.assert_awaited_once_with(
            friendship_request_repository=mocked_friendship_request_repository_instance,
            friendship_request_id=friendship_request_id,
            user_id=user_id,
        )
        mocked_friendship_request_repository_instance.update_status.assert_not_awaited()
