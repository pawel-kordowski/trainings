from datetime import datetime

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from tests.factories.users import UserFactory


class TrainingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.Training
        sqlalchemy_session_persistence = "commit"

    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    name = "Test"
    user = SubFactory(UserFactory)
    visibility = None
