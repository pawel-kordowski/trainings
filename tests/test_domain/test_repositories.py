from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select

from app import models
from app.database import get_session, engine
from app.domain.exceptions import EmailAlreadyExists
from app.domain.repositories import PostgresRepository
from app.domain import entities
from tests.factories import (
    TrainingFactory,
    ReactionFactory,
    UserFactory,
    FriendshipFactory,
)
from tests.sqlalchemy_helpers import QueryCounter


async def test_get_user_training_by_id_returns_none_when_user_id_not_matching(training):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                await repository.get_user_training_by_id(
                    user_id=uuid4(), training_id=training.id
                )
                is None
            )
        assert query_counter.count == 1


async def test_get_user_training_by_id_returns_none_when_training_id_not_matching(
    user, training
):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert (
                await repository.get_user_training_by_id(
                    user_id=user.id, training_id=uuid4()
                )
                is None
            )
        assert query_counter.count == 1


async def test_get_user_training_by_id_existing_returns_training(user, training):
    # another user training
    TrainingFactory()
    # another training of the current user
    TrainingFactory(user=user)
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_training_by_id(
                user_id=user.id, training_id=training.id
            ) == entities.Training(
                id=training.id,
                start_time=training.start_time,
                end_time=training.end_time,
                name=training.name,
                user_id=user.id,
            )
        assert query_counter.count == 1


async def test_get_user_trainings_returns_empty_list_when_no_trainings_for_user(user):
    # another user training
    TrainingFactory()
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_trainings(user_id=user.id) == []
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

    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_trainings(user_id=user.id) == [
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

    async with get_session() as s:
        repository = PostgresRepository(s)
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


async def test_get_reaction_count_by_training_ids(db_session):
    training_1 = TrainingFactory()
    ReactionFactory.create_batch(10, training=training_1)
    training_2 = TrainingFactory()
    training_3 = TrainingFactory()
    ReactionFactory.create_batch(5, training=training_3)

    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_reaction_count_by_training_ids(
                [training_1.id, training_2.id, training_3.id, uuid4()]
            ) == [10, 0, 5, 0]
        assert query_counter.count == 1


async def test_get_reactions_by_training_ids(db_session):
    training_1 = TrainingFactory()
    created_at_base = datetime.fromisoformat("2020-10-10T10:00:00")
    training_1_reaction_1 = ReactionFactory(
        training=training_1, created_at=created_at_base
    )
    training_1_reaction_2 = ReactionFactory(
        training=training_1, created_at=created_at_base - timedelta(minutes=1)
    )
    training_1_reaction_3 = ReactionFactory(
        training=training_1, created_at=created_at_base + timedelta(minutes=1)
    )
    training_1_reactions = [
        training_1_reaction_3,
        training_1_reaction_1,
        training_1_reaction_2,
    ]
    training_2 = TrainingFactory()
    training_3 = TrainingFactory()
    training_3_reaction = ReactionFactory(training=training_3)

    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_reactions_by_training_ids(
                [training_1.id, training_2.id, training_3.id, uuid4()]
            ) == [
                [
                    entities.Reaction(
                        id=reaction.id,
                        reaction_type=reaction.reaction_type,
                        user_id=reaction.user_id,
                    )
                    for reaction in training_1_reactions
                ],
                [],
                [
                    entities.Reaction(
                        id=training_3_reaction.id,
                        reaction_type=training_3_reaction.reaction_type,
                        user_id=training_3_reaction.user_id,
                    )
                ],
                [],
            ]
        assert query_counter.count == 1


async def test_get_users_by_ids(db_session):
    users = UserFactory.create_batch(3)

    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_users_by_ids([user.id for user in users]) == [
                entities.User(id=user.id, email=user.email) for user in users
            ]
        assert query_counter.count == 1


async def test_get_user_friends_ids_no_friends(user):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_friends_ids(user.id) == set()
        assert query_counter.count == 1


async def test_get_user_friends_ids_friends(user):
    friendship_1 = FriendshipFactory(user_1=user)
    friendship_2 = FriendshipFactory(user_1=user)
    FriendshipFactory()

    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_friends_ids(user.id) == {
                friendship_1.user_2.id,
                friendship_2.user_2.id,
            }
        assert query_counter.count == 1


async def test_get_training_by_id_not_existing(training):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_training_by_id(uuid4()) is None
        assert query_counter.count == 1


async def test_get_training_by_id_existing(training):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_training_by_id(
                training.id
            ) == entities.Training(
                id=training.id,
                name=training.name,
                start_time=training.start_time,
                end_time=training.end_time,
                user_id=training.user_id,
            )
        assert query_counter.count == 1


async def test_create_user(db_session):
    email = "email"
    hashed_password = "hashed_password"
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            user = await repository.create_user(
                email=email, hashed_password=hashed_password
            )
        assert query_counter.count == 1

    sql = select(models.User)
    users_from_db = db_session.execute(sql).all()
    assert len(users_from_db) == 1
    user_from_db = users_from_db[0][0]
    assert user_from_db.id == user.id
    assert user_from_db.email == user.email == email
    assert user_from_db.hashed_password == hashed_password


async def test_create_user_already_exists(user):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            with pytest.raises(EmailAlreadyExists):
                await repository.create_user(
                    email=user.email, hashed_password="hashed_password"
                )
        assert query_counter.count == 1


async def test_get_user__by_email_not_existing():
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_by_email(email="email") is None
        assert query_counter.count == 1


async def test_get_user_by_email_existing(user):
    async with get_session() as s:
        repository = PostgresRepository(s)
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_by_email(
                email=user.email
            ) == entities.UserWithHashedPassword(
                id=user.id, email=user.email, hashed_password=user.hashed_password
            )
        assert query_counter.count == 1
