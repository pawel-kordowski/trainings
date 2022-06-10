from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.jwt_tokens import create_access_token


@patch("app.graphql.mutations.trainings.TrainingService", autospec=True)
class TestCreateTraining:
    name = "New training"
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")

    def get_query(self):
        return f"""
        mutation {{
            createTraining(
                input: {{
                    name: "{self.name}"
                    startTime: "{self.start_time.isoformat()}"
                    endTime: "{self.end_time.isoformat()}"
                }}
            ) {{
                id
                name
                startTime
                endTime
            }}
        }}
        """

    def test_requires_authorization(self, mocked_training_service, client):
        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"] is None
        assert response_json["errors"][0]["message"] == "User is not authenticated"

    def test_calls_training_service_create_training(
        self, mocked_training_service, client
    ):
        user_id = uuid4()
        training = entities.Training(
            id=uuid4(),
            name=self.name,
            start_time=self.start_time,
            end_time=self.end_time,
            user_id=user_id,
        )
        mocked_training_service.create_training.return_value = training

        response = client.post(
            "/graphql",
            json={"query": self.get_query()},
            headers={"Authorization": f"Bearer {create_access_token(user_id)}"},
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["createTraining"] == {
            "id": str(training.id),
            "name": training.name,
            "startTime": training.start_time.isoformat(),
            "endTime": training.end_time.isoformat(),
        }

        mocked_training_service.create_training.assert_awaited_once_with(
            user_id=user_id,
            name=self.name,
            start_time=self.start_time,
            end_time=self.end_time,
        )
