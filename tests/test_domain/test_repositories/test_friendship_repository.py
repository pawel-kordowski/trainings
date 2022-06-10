from uuid import uuid4

from app.database import engine
from app.domain.repositories.friendship_repository import FriendshipRepository
from tests.test_domain.test_repositories.factories import FriendshipFactory
from tests.test_domain.test_repositories.sqlalchemy_helpers import QueryCounter


async def test_get_user_friends_ids_no_friends(user):
    async with FriendshipRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_friends_ids(user.id) == set()
        assert query_counter.count == 1


async def test_get_user_friends_ids_friends(user):
    friendship_1 = FriendshipFactory(user_1=user)
    friendship_2 = FriendshipFactory(user_1=user)
    FriendshipFactory()

    async with FriendshipRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_user_friends_ids(user.id) == {
                friendship_1.user_2.id,
                friendship_2.user_2.id,
            }
        assert query_counter.count == 1


async def test_are_users_friends_returns_true_when_users_are_friends(db_session):
    friendship = FriendshipFactory()

    async with FriendshipRepository() as repository:
        assert (
            await repository.are_users_friends(
                user_1_id=friendship.user_1_id, user_2_id=friendship.user_2_id
            )
            is True
        )


async def test_are_users_friends_returns_false_when_users_are_not_friends(db_session):
    friendship_1, friendship_2 = FriendshipFactory.create_batch(size=2)

    async with FriendshipRepository() as repository:
        assert (
            await repository.are_users_friends(
                user_1_id=uuid4(), user_2_id=friendship_1.user_2_id
            )
            is False
        )
        assert (
            await repository.are_users_friends(
                user_1_id=friendship_1.user_1_id, user_2_id=uuid4()
            )
            is False
        )
        assert (
            await repository.are_users_friends(
                user_1_id=friendship_1.user_1_id, user_2_id=friendship_2.user_2_id
            )
            is False
        )
