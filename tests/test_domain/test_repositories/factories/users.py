from factory import Sequence, RelatedFactory
from factory.alchemy import SQLAlchemyModelFactory

from app import models
from app.passwords import get_password_hash


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session_persistence = "commit"

    email = Sequence(lambda n: f"user_{n}@test.com")
    hashed_password = get_password_hash("password")
    profile = RelatedFactory(
        "tests.test_domain.test_repositories.factories.profiles.ProfileFactory",
        factory_related_name="user",
    )
