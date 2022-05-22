from datetime import datetime

from factory import Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app.enums import ReactionTypeEnum


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session_persistence = "commit"

    email = Sequence(lambda n: f"user_{n}@test.com")
    hashed_password = "hashed_password"


class TrainingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Training
        sqlalchemy_session_persistence = "commit"

    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    name = "Test"
    user = SubFactory(UserFactory)


class ReactionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Reaction
        sqlalchemy_session_persistence = "commit"

    user = SubFactory(UserFactory)
    training = SubFactory(TrainingFactory)
    reaction_type = ReactionTypeEnum.like
    created_at = datetime.fromisoformat("2020-10-10T10:00:00")
