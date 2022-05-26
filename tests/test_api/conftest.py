import pytest
from starlette.testclient import TestClient

from app.api import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
