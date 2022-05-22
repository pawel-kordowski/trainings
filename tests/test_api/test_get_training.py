from datetime import datetime
from uuid import uuid4

from app.enums import ReactionTypeEnum
from app.jwt_tokens import create_access_token
from app.models import Reaction, Training, User


def test_query_training_requires_authorization(client):
    query = f"""
    {{
        training(id: "{str(uuid4())}"){{
            name
        }}
    }}
    """
    response = client.post(
        "/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["training"] is None
    assert response_json["errors"][0]["message"] == "User is not authenticated"


def test_query_not_existing_training(client):
    query = f"""
    {{
        training(id: "{str(uuid4())}"){{
            name
        }}
    }}
    """
    response = client.post(
        "/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {create_access_token(uuid4())}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["training"] is None


def test_query_existing_training(client, db_session, user):
    uuid = uuid4()
    start_time = "2020-10-10T10:00:00"
    end_time = "2020-10-10T11:00:00"
    name = "name"
    training = Training(
        id=uuid,
        user_id=user.id,
        start_time=start_time,
        end_time=end_time,
        name=name,
    )
    another_training = Training(
        id=uuid4(),
        user_id=user.id,
        start_time=start_time,
        end_time=end_time,
        name=name,
    )
    extra_users = []
    reactions = []
    for n in range(4):
        _user = User(
            id=uuid4(),
            email=f"_user_{n}@test.com",
            hashed_password="hashed_password",
        )
        extra_users.append(_user)
        reactions.extend(
            [
                Reaction(
                    id=uuid4(),
                    user_id=_user.id,
                    training_id=training.id,
                    reaction_type=ReactionTypeEnum.like,
                    created_at=datetime.fromisoformat("2020-10-10T10:00:00")
                ),
                Reaction(
                    id=uuid4(),
                    user_id=_user.id,
                    training_id=another_training.id,
                    reaction_type=ReactionTypeEnum.like,
                    created_at=datetime.fromisoformat("2020-10-10T10:00:00")
                ),
            ]
        )
    db_session.add_all([training, another_training, *extra_users, *reactions])
    db_session.commit()

    query = f"""
    {{
        training(id: "{str(uuid)}"){{
            id
            startTime
            endTime
            name
            reactionsCount
        }}
    }}
    """

    response = client.post(
        "/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["training"] == {
        "id": str(uuid),
        "startTime": start_time,
        "endTime": end_time,
        "name": name,
        "reactionsCount": 4,
    }
