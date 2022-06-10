from uuid import uuid4

import pytest
from sqlalchemy import select

from app import models
from app.database import engine
from app.domain import entities
from app.domain.exceptions import EmailAlreadyExists
from app.domain.repositories.user_repository import UserRepository
from tests.test_domain.test_repositories.factories import UserFactory
from tests.test_domain.test_repositories.sqlalchemy_helpers import QueryCounter


async def test_get_users_by_ids(db_session):
    users = UserFactory.create_batch(3)

    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_users_by_ids([user.id for user in users]) == [
                entities.User(id=user.id, email=user.email) for user in users
            ]
        assert query_counter.count == 1


async def test_create_user(db_session):
    email = "email"
    hashed_password = "hashed_password"
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            user = await repository.create_user(
                email=email, hashed_password=hashed_password
            )
        assert query_counter.count == 2

    sql = select(models.User)
    users_from_db = db_session.execute(sql).all()
    assert len(users_from_db) == 1
    user_from_db = users_from_db[0][0]
    assert user_from_db.id == user.id
    assert user_from_db.email == user.email == email
    assert user_from_db.hashed_password == hashed_password

    sql = select(models.Profile)
    profiles_from_db = db_session.execute(sql).all()
    assert len(profiles_from_db) == 1
    assert profiles_from_db[0][0].user_id == user.id


async def test_create_user_already_exists(user):
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            with pytest.raises(EmailAlreadyExists):
                await repository.create_user(
                    email=user.email, hashed_password="hashed_password"
                )
        assert query_counter.count == 1


async def test_get_user_by_email_not_existing():
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_by_email(email="email") is None
        assert query_counter.count == 1


async def test_get_user_by_email_existing(user):
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_by_email(
                email=user.email
            ) == entities.UserWithHashedPassword(
                id=user.id, email=user.email, hashed_password=user.hashed_password
            )
        assert query_counter.count == 1


async def test_does_user_with_id_exist_not_existing():
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.does_user_with_id_exist(user_id=uuid4()) is False
        assert query_counter.count == 1


async def test_does_user_with_id_exist_existing(user):
    async with UserRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.does_user_with_id_exist(user_id=user.id) is True
        assert query_counter.count == 1
