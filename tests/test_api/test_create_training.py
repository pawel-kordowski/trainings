from datetime import datetime
from unittest.mock import ANY

from sqlalchemy import select

from app.jwt_tokens import create_access_token
from app.models import Training


def test_add_training_requires_authorization(client):
    query = """
    mutation {
        createTraining(
            input:{
                name: "New training"
                startTime: "2020-10-10T10:00:00"
                endTime: "2020-10-10T11:00:00"
            }
        ) {
            id
        }
    }
    """
    response = client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"] is None
    assert response_json["errors"][0]["message"] == "User is not authenticated"


def test_add_training_saves_training_in_db(client, db_session, user):
    name = "New training"
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    query = f"""
    mutation {{
        createTraining(
            input:{{
                name: "{name}"
                startTime: "{start_time.isoformat()}"
                endTime: "{end_time.isoformat()}"
            }}
        ) {{
            id
            name
            startTime
            endTime
        }}
    }}
    """
    response = client.post(
        "/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createTraining"] == {
        "id": ANY,
        "name": name,
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
    }

    sql = select(Training)
    trainings_from_db = db_session.execute(sql).all()
    assert len(trainings_from_db) == 1
    training = trainings_from_db[0][0]
    assert training.name == name
    assert training.start_time == start_time
    assert training.end_time == end_time
