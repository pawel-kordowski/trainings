from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from tests.factories.users import UserFactory


class FriendshipFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Friendship
        sqlalchemy_session_persistence = "commit"

    user_1 = SubFactory(UserFactory)
    user_2 = SubFactory(UserFactory)
