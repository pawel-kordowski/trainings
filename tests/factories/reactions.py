from datetime import datetime

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app.enums import ReactionTypeEnum
from tests.factories.trainings import TrainingFactory
from tests.factories.users import UserFactory


class ReactionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Reaction
        sqlalchemy_session_persistence = "commit"

    user = SubFactory(UserFactory)
    training = SubFactory(TrainingFactory)
    reaction_type = ReactionTypeEnum.like
    created_at = datetime.fromisoformat("2020-10-10T10:00:00")
