from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models, enums
from tests.test_domain.test_repositories.factories import UserFactory


class FriendshipRequestFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.FriendshipRequest
        sqlalchemy_session_persistence = "commit"

    sender = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
    status = enums.FriendshipRequestStatusEnum.pending
