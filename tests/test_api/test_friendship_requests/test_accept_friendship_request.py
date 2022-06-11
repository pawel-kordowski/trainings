from unittest.mock import patch
from uuid import uuid4, UUID

from app.domain.services.exceptions import AppError
from app.jwt_tokens import create_access_token


@patch(
    "app.graphql.mutations.friendship_requests.FriendshipRequestService", autospec=True
)
class TestAcceptFriendshipRequest:
    def get_query(self, friendship_request_id: UUID):
        return f"""
        mutation {{
            acceptFriendshipRequest(
                input: {{
                    friendshipRequestId: "{friendship_request_id}"
                }}
            ) {{
                __typename
                ... on Error {{
                    message
                }}
                ... on OK {{
                    message
                }}
            }}
        }}
        """

    def test_requires_authorization(self, mocked_friendship_request_service, client):
        response = client.post(
            "/graphql", json={"query": self.get_query(friendship_request_id=uuid4())}
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"] is None
        assert response_json["errors"][0]["message"] == "User is not authenticated"

    def test_returns_error_when_exception_occur(
        self, mocked_friendship_request_service, client
    ):
        error_message = "Error message"
        mocked_friendship_request_service.accept_friendship_request.side_effect = (
            AppError(message=error_message)
        )
        friendship_request_id = uuid4()
        user_id = uuid4()

        response = client.post(
            "/graphql",
            json={"query": self.get_query(friendship_request_id=friendship_request_id)},
            headers={"Authorization": f"Bearer {create_access_token(user_id=user_id)}"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["acceptFriendshipRequest"] == {
            "__typename": "Error",
            "message": error_message,
        }
        mocked_friendship_request_service.accept_friendship_request.assert_awaited_once_with(  # noqa
            user_id=user_id, friendship_request_id=friendship_request_id
        )

    def test_returns_ok_when_no_exception_occur(
        self, mocked_friendship_request_service, client
    ):
        friendship_request_id = uuid4()
        user_id = uuid4()

        response = client.post(
            "/graphql",
            json={"query": self.get_query(friendship_request_id=friendship_request_id)},
            headers={"Authorization": f"Bearer {create_access_token(user_id=user_id)}"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["acceptFriendshipRequest"] == {
            "__typename": "OK",
            "message": "OK",
        }
        mocked_friendship_request_service.accept_friendship_request.assert_awaited_once_with(  # noqa
            user_id=user_id, friendship_request_id=friendship_request_id
        )
