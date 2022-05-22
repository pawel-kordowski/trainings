from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config, models
from app.api import app
from tests.factories import UserFactory, TrainingFactory


@pytest.fixture(scope="session")
def engine():
    return create_engine(
        f"postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
        f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}",
        echo=True,
        future=True,
    )


@pytest.fixture(autouse=True)
def setup_database(engine):
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)

    yield

    models.Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, setup_database):
    session_factory = sessionmaker(engine, autocommit=False, autoflush=False)
    with session_factory() as session:
        from factory.alchemy import SQLAlchemyModelFactory

        for cls in SQLAlchemyModelFactory.__subclasses__():
            cls._meta.sqlalchemy_session = session
        yield session


@pytest.fixture
def user(db_session):
    return UserFactory()


@pytest.fixture
def training(db_session, user):
    return TrainingFactory(user=user)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
