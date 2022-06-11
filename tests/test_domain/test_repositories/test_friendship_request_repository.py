from datetime import timedelta
from uuid import uuid4

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from app import enums, models, helpers
from app.domain import entities
from app.domain.repositories.friendship_request_repository import (
    FriendshipRequestRepository,
)
from app.helpers import get_utc_now
from tests.test_domain.test_repositories.factories import (
    FriendshipRequestFactory,
    UserFactory,
)


async def test_does_pending_request_exist_not_exists(db_session):
    friendship_request = FriendshipRequestFactory(
        status=enums.FriendshipRequestStatusEnum.accepted
    )
    FriendshipRequestFactory(
        sender=friendship_request.sender,
        receiver=friendship_request.receiver,
        status=enums.FriendshipRequestStatusEnum.rejected,
    )
    FriendshipRequestFactory(
        sender=friendship_request.sender,
        receiver=friendship_request.receiver,
        status=enums.FriendshipRequestStatusEnum.cancelled,
    )
    FriendshipRequestFactory(
        sender=friendship_request.sender,
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    FriendshipRequestFactory(
        receiver=friendship_request.receiver,
        status=enums.FriendshipRequestStatusEnum.pending,
    )

    async with FriendshipRequestRepository() as friendship_request_repository:
        assert (
            await friendship_request_repository.does_pending_request_exist(
                user_1_id=friendship_request.sender.id,
                user_2_id=friendship_request.receiver.id,
            )
            is False
        )
        assert (
            await friendship_request_repository.does_pending_request_exist(
                user_1_id=friendship_request.receiver.id,
                user_2_id=friendship_request.sender.id,
            )
            is False
        )


async def test_does_pending_request_exist_exists(db_session):
    friendship_request = FriendshipRequestFactory(
        status=enums.FriendshipRequestStatusEnum.pending
    )

    async with FriendshipRequestRepository() as friendship_request_repository:
        assert (
            await friendship_request_repository.does_pending_request_exist(
                user_1_id=friendship_request.sender.id,
                user_2_id=friendship_request.receiver.id,
            )
            is True
        )
        assert (
            await friendship_request_repository.does_pending_request_exist(
                user_1_id=friendship_request.receiver.id,
                user_2_id=friendship_request.sender.id,
            )
            is True
        )


@freeze_time("2020-10-11 10:00:00")
async def test_create_pending_request(db_session):
    sender, receiver = UserFactory.create_batch(size=2)
    async with FriendshipRequestRepository() as friendship_request_repository:
        friendship_request = await friendship_request_repository.create_pending_request(
            sender_id=sender.id, receiver_id=receiver.id
        )

    sql = select(models.FriendshipRequest)
    friendship_requests_from_db = db_session.execute(sql).scalars().all()
    assert len(friendship_requests_from_db) == 1
    friendship_request_from_db = friendship_requests_from_db[0]
    assert friendship_request.id == friendship_request_from_db.id
    assert (
        friendship_request.sender_id
        == sender.id
        == friendship_request_from_db.sender_id
    )
    assert (
        friendship_request.receiver_id
        == receiver.id
        == friendship_request_from_db.receiver_id
    )
    assert (
        friendship_request.status
        == enums.FriendshipRequestStatusEnum.pending
        == friendship_request_from_db.status
    )
    assert (
        friendship_request.timestamp
        == get_utc_now()
        == friendship_request_from_db.timestamp
    )


async def test_get_pending_requests_sent_by_user(db_session):
    sender = UserFactory()
    now = helpers.get_utc_now()
    friendship_request_1 = FriendshipRequestFactory(
        sender=sender, timestamp=now, status=enums.FriendshipRequestStatusEnum.pending
    )
    friendship_request_2 = FriendshipRequestFactory(
        sender=sender,
        timestamp=now + timedelta(minutes=1),
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    friendship_request_3 = FriendshipRequestFactory(
        sender=sender,
        timestamp=now - timedelta(minutes=1),
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    FriendshipRequestFactory(
        sender=sender, status=enums.FriendshipRequestStatusEnum.accepted
    )
    FriendshipRequestFactory(
        sender=sender, status=enums.FriendshipRequestStatusEnum.cancelled
    )
    FriendshipRequestFactory(
        sender=sender, status=enums.FriendshipRequestStatusEnum.rejected
    )
    FriendshipRequestFactory(
        receiver=sender, status=enums.FriendshipRequestStatusEnum.pending
    )

    async with FriendshipRequestRepository() as repository:
        assert await repository.get_pending_requests_sent_by_user(
            user_id=sender.id
        ) == [
            entities.FriendshipRequest.from_model(friendship_request)
            for friendship_request in [
                friendship_request_3,
                friendship_request_1,
                friendship_request_2,
            ]
        ]


async def test_get_pending_requests_sent_by_user_no_results():
    async with FriendshipRequestRepository() as repository:
        assert await repository.get_pending_requests_sent_by_user(user_id=uuid4()) == []


async def test_get_pending_requests_received_by_user(db_session):
    receiver = UserFactory()
    now = helpers.get_utc_now()
    friendship_request_1 = FriendshipRequestFactory(
        receiver=receiver,
        timestamp=now,
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    friendship_request_2 = FriendshipRequestFactory(
        receiver=receiver,
        timestamp=now + timedelta(minutes=1),
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    friendship_request_3 = FriendshipRequestFactory(
        receiver=receiver,
        timestamp=now - timedelta(minutes=1),
        status=enums.FriendshipRequestStatusEnum.pending,
    )
    FriendshipRequestFactory(
        receiver=receiver, status=enums.FriendshipRequestStatusEnum.accepted
    )
    FriendshipRequestFactory(
        receiver=receiver, status=enums.FriendshipRequestStatusEnum.cancelled
    )
    FriendshipRequestFactory(
        receiver=receiver, status=enums.FriendshipRequestStatusEnum.rejected
    )
    FriendshipRequestFactory(
        sender=receiver, status=enums.FriendshipRequestStatusEnum.pending
    )

    async with FriendshipRequestRepository() as repository:
        assert await repository.get_pending_requests_received_by_user(
            user_id=receiver.id
        ) == [
            entities.FriendshipRequest.from_model(friendship_request)
            for friendship_request in [
                friendship_request_3,
                friendship_request_1,
                friendship_request_2,
            ]
        ]


async def test_get_pending_requests_received_by_user_no_results():
    async with FriendshipRequestRepository() as repository:
        assert (
            await repository.get_pending_requests_received_by_user(user_id=uuid4())
            == []
        )


@pytest.mark.parametrize(
    "status",
    (
        enums.FriendshipRequestStatusEnum.accepted,
        enums.FriendshipRequestStatusEnum.rejected,
        enums.FriendshipRequestStatusEnum.cancelled,
        enums.FriendshipRequestStatusEnum.pending,
    ),
)
async def test_update_status(status, db_session):
    friendship_request = FriendshipRequestFactory(
        status=enums.FriendshipRequestStatusEnum.pending
    )

    async with FriendshipRequestRepository() as repository:
        await repository.update_status(
            friendship_request_id=friendship_request.id, status=status
        )

    db_session.refresh(friendship_request)
    assert friendship_request.status == status
