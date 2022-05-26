from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.jwt_tokens import create_access_token


def test_create_training_requires_authorization(client):
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


@patch("app.graphql.mutations.trainings.TrainingService", autospec=True)
def test_create_training_calls_training_service_create_training(
    mocked_training_service, client
):
    name = "New training"
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    user_id = uuid4()
    training_id = uuid4()
    mocked_training_service.create_training.return_value = entities.Training(
        id=training_id,
        name=name,
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
    )
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
        headers={"Authorization": f"Bearer {create_access_token(user_id)}"},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createTraining"] == {
        "id": str(training_id),
        "name": name,
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
    }

    mocked_training_service.create_training.assert_awaited_once_with(
        user_id=user_id, name=name, start_time=start_time, end_time=end_time
    )
