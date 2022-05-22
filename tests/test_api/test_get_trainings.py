from datetime import datetime, timedelta
from uuid import uuid4

from app.database import engine
from app.enums import ReactionTypeEnum
from app.jwt_tokens import create_access_token
from app.models import Reaction, Training, User
from tests.sqlalchemy_helpers import QueryCounter


def test_query_trainings_requires_authorization(client):
    query = """
    {
        trainings{
            name
        }
    }
    """
    response = client.post(
        "/graphql",
        json={"query": query},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"] is None
    assert response_json["errors"][0]["message"] == "User is not authenticated"


def test_query_not_existing_trainings(client):
    query = """
    {
        trainings{
            name
        }
    }
    """
    response = client.post(
        "/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {create_access_token(uuid4())}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["trainings"] == []


def test_query_user_trainings(client, db_session, user):
    start_time_base = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time_base = start_time_base + timedelta(minutes=10)
    trainings = [
        Training(
            id=uuid4(),
            user_id=user.id,
            start_time=start_time_base + n * timedelta(minutes=20),
            end_time=end_time_base + n * timedelta(minutes=20),
            name=f"Training {n}",
        )
        for n in range(10)
    ]
    reactions = []
    reactions_by_training_id = {}
    users_by_id = {}
    for n, training in enumerate(trainings):
        _user = User(
            id=uuid4(),
            email=f"email_{n}@test.com",
            hashed_password="hashed_password",
        )
        users_by_id[_user.id] = _user
        training_reactions = [
            Reaction(
                id=uuid4(),
                user_id=_user.id,
                training_id=training.id,
                reaction_type=ReactionTypeEnum.like,
                created_at=datetime.fromisoformat("2020-10-10T10:00:00"),
            )
            for _ in range(n)
        ]
        reactions_by_training_id[training.id] = training_reactions
        reactions.extend(training_reactions)
    another_user = User(
        id=uuid4(),
        email="another@test.com",
        hashed_password="hashed_password",
    )
    another_training = Training(
        id=uuid4(),
        user_id=another_user.id,
        start_time=start_time_base,
        end_time=end_time_base,
        name="Training",
    )
    db_session.add_all(
        [*trainings, *reactions, *users_by_id.values(), another_user, another_training]
    )
    db_session.commit()

    query = """
    {
        trainings{
            id
            name
            startTime
            endTime
            reactionsCount
            reactions{
                id
                reactionType
                user{
                    id
                    email
                }
            }
        }
    }
    """

    with QueryCounter(engine.sync_engine) as query_counter:
        response = client.post(
            "/graphql",
            json={"query": query},
            headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["trainings"] == [
        {
            "id": str(training.id),
            "name": training.name,
            "startTime": training.start_time.isoformat(),
            "endTime": training.end_time.isoformat(),
            "reactionsCount": len(trainings) - n - 1,
            "reactions": [
                {
                    "id": str(reaction.id),
                    "reactionType": "like",
                    "user": {
                        "id": str(users_by_id[reaction.user_id].id),
                        "email": users_by_id[reaction.user_id].email,
                    },
                }
                for reaction in reactions_by_training_id[training.id]
            ],
        }
        for n, training in enumerate(reversed(trainings))
    ]
    assert query_counter.count == 4
