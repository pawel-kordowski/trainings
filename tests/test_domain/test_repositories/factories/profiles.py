from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app.enums import TrainingVisibilityEnum
from tests.test_domain.test_repositories.factories import UserFactory


class ProfileFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Profile
        sqlalchemy_session_persistence = "commit"

    user = SubFactory(UserFactory)
    training_visibility = TrainingVisibilityEnum.public
