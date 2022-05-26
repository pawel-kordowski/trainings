from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select

from app import models
from app.database import engine
from app.domain import entities
from app.domain.repositories.training_repository import TrainingRepository
from app.enums import TrainingVisibilityEnum
from tests.test_domain.test_repositories.factories import (
    TrainingFactory,
    FriendshipFactory,
)
from tests.test_domain.test_repositories.sqlalchemy_helpers import QueryCounter


async def test_get_training_by_id_returns_none_when_training_id_not_matching(
    user, training
):
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                await repository.get_training_by_id(
                    request_user_id=user.id, training_id=uuid4()
                )
                is None
            )
        assert query_counter.count == 1


async def test_get_training_by_id_existing_returns_training(user, training):
    # another user training
    TrainingFactory()
    # another training of the current user
    TrainingFactory(user=user)
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_training_by_id(
                request_user_id=user.id, training_id=training.id
            ) == entities.Training(
                id=training.id,
                start_time=training.start_time,
                end_time=training.end_time,
                name=training.name,
                user_id=user.id,
            )
        assert query_counter.count == 1


@pytest.mark.parametrize(
    "training_visibility,profile_training_visibility,expected_count",
    (
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.private, 0),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.only_friends, 0),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.public, 0),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.private, 0),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.only_friends, 0),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.public, 0),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.public, 1),
        (None, TrainingVisibilityEnum.private, 0),
        (None, TrainingVisibilityEnum.only_friends, 0),
        (None, TrainingVisibilityEnum.public, 1),
    ),
)
async def test_get_user_trainings_takes_permissions_into_account_not_friends(
    user, training_visibility, profile_training_visibility, expected_count
):
    # another user training
    training = TrainingFactory(
        visibility=training_visibility,
        user__profile__training_visibility=profile_training_visibility,
    )
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                len(
                    await repository.get_user_trainings(
                        user_id=training.user.id, request_user_id=user.id
                    )
                )
                == expected_count
            )
        assert query_counter.count == 1


@pytest.mark.parametrize(
    "training_visibility,profile_training_visibility,expected_count",
    (
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.private, 0),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.only_friends, 0),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.public, 0),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.public, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.public, 1),
        (None, TrainingVisibilityEnum.private, 0),
        (None, TrainingVisibilityEnum.only_friends, 1),
        (None, TrainingVisibilityEnum.public, 1),
    ),
)
async def test_get_user_trainings_takes_permissions_into_account_friends(
    user, training_visibility, profile_training_visibility, expected_count
):
    # another user training
    training = TrainingFactory(
        visibility=training_visibility,
        user__profile__training_visibility=profile_training_visibility,
    )
    FriendshipFactory(user_1=user, user_2=training.user)
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                len(
                    await repository.get_user_trainings(
                        user_id=training.user.id, request_user_id=user.id
                    )
                )
                == expected_count
            )
        assert query_counter.count == 1


@pytest.mark.parametrize(
    "training_visibility,profile_training_visibility,expected_count",
    (
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.private, TrainingVisibilityEnum.public, 1),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.only_friends, TrainingVisibilityEnum.public, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.private, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.only_friends, 1),
        (TrainingVisibilityEnum.public, TrainingVisibilityEnum.public, 1),
        (None, TrainingVisibilityEnum.private, 1),
        (None, TrainingVisibilityEnum.only_friends, 1),
        (None, TrainingVisibilityEnum.public, 1),
    ),
)
async def test_get_user_trainings_takes_permissions_into_account_own_training(
    db_session, training_visibility, profile_training_visibility, expected_count
):
    # another user training
    training = TrainingFactory(
        visibility=training_visibility,
        user__profile__training_visibility=profile_training_visibility,
    )
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                len(
                    await repository.get_user_trainings(
                        user_id=training.user.id, request_user_id=training.user.id
                    )
                )
                == expected_count
            )
        assert query_counter.count == 1


async def test_get_user_trainings_returns_ordered_list_when_trainings(user):
    # another user training
    TrainingFactory()
    # current user trainings
    training_1 = TrainingFactory(
        user=user,
        start_time=datetime.fromisoformat("2020-10-10T10:00:00"),
    )
    training_2 = TrainingFactory(
        user=user,
        start_time=datetime.fromisoformat("2020-10-11T10:00:00"),
    )
    training_3 = TrainingFactory(
        user=user,
        start_time=datetime.fromisoformat("2020-10-09T10:00:00"),
    )
    ordered_trainings = [training_2, training_1, training_3]

    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_trainings(
                user_id=user.id, request_user_id=user.id
            ) == [
                entities.Training(
                    id=training.id,
                    start_time=training.start_time,
                    end_time=training.end_time,
                    name=training.name,
                    user_id=training.user_id,
                )
                for training in ordered_trainings
            ]
        assert query_counter.count == 1


async def test_create_training(db_session, user):
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    name = "name"

    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            training = await repository.create_training(
                user_id=user.id, start_time=start_time, end_time=end_time, name=name
            )
        assert query_counter.count == 1

    sql = select(models.Training)

    trainings_from_db = db_session.execute(sql).all()
    assert len(trainings_from_db) == 1
    training_from_db = trainings_from_db[0][0]
    assert training_from_db.id == training.id
    assert start_time == training.start_time == training_from_db.start_time
    assert end_time == training.end_time == training_from_db.end_time
    assert name == training.name == training_from_db.name
    assert user.id == training.user_id == training_from_db.user_id


async def test_get_training_by_id_not_existing(training):
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_training_by_id(uuid4(), uuid4()) is None
        assert query_counter.count == 1


async def test_get_training_by_id_existing(training):
    async with TrainingRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_training_by_id(
                training.user_id, training.id
            ) == entities.Training(
                id=training.id,
                name=training.name,
                start_time=training.start_time,
                end_time=training.end_time,
                user_id=training.user_id,
            )
        assert query_counter.count == 1
