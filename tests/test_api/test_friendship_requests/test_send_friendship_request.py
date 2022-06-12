from datetime import datetime
from unittest.mock import patch
from uuid import uuid4, UUID

from app.domain.entities import FriendshipRequest, User
from app.domain.services.exceptions import AppError
from app.enums import FriendshipRequestStatusEnum
from app.jwt_tokens import create_access_token


@patch(
    "app.graphql.mutations.friendship_requests.FriendshipRequestService", autospec=True
)
class TestSendFriendshipRequest:
    @staticmethod
    def get_query(user_id: UUID):
        return f"""
        mutation {{
            sendFriendshipRequest(
                input: {{
                    userId: "{user_id}"
                }}
            ) {{
                __typename
                ... on FriendshipRequest{{
                    id
                    senderId
                    receiverId
                    timestamp
                    sender {{
                        id
                        email
                    }}
                    receiver {{
                        id
                        email
                    }}
                }}
                ... on Error {{
                    message
                }}
            }}
        }}
        """

    @patch("app.graphql.data_loaders.users.UserService", autospec=True)
    def test_successful(
        self, mocked_user_service, mocked_friendship_request_service, client
    ):
        sender = User(id=uuid4(), email="sender@test.com")
        receiver = User(id=uuid4(), email="receiver@test.com")
        mocked_user_service.get_users_by_ids.return_value = [sender, receiver]
        friendship_request = FriendshipRequest(
            id=uuid4(),
            sender_id=sender.id,
            receiver_id=receiver.id,
            status=FriendshipRequestStatusEnum.pending,
            timestamp=datetime.utcnow(),
        )
        mocked_friendship_request_service.create_friendship_request.return_value = (
            friendship_request
        )

        response = client.post(
            "/graphql",
            json={"query": self.get_query(user_id=receiver.id)},
            headers={
                "Authorization": f"Bearer {create_access_token(user_id=sender.id)}"
            },
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["sendFriendshipRequest"] == {
            "__typename": "FriendshipRequest",
            "id": str(friendship_request.id),
            "senderId": str(sender.id),
            "receiverId": str(receiver.id),
            "timestamp": friendship_request.timestamp.isoformat(),
            "sender": {"id": str(sender.id), "email": sender.email},
            "receiver": {"id": str(receiver.id), "email": receiver.email},
        }
        mocked_user_service.get_users_by_ids.assert_awaited_once_with(
            [sender.id, receiver.id]
        )
        mocked_friendship_request_service.create_friendship_request.assert_awaited_once_with(  # noqa
            sender_id=sender.id, receiver_id=receiver.id
        )

    def test_requires_authorization(self, mocked_friendship_request_service, client):
        response = client.post(
            "/graphql", json={"query": self.get_query(user_id=uuid4())}
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"] is None
        assert response_json["errors"][0]["message"] == "User is not authenticated"

    def test_returns_error_when_exception_occur(
        self, mocked_friendship_request_service, client
    ):
        error_message = "Error message"
        mocked_friendship_request_service.create_friendship_request.side_effect = (
            AppError(message=error_message)
        )

        response = client.post(
            "/graphql",
            json={"query": self.get_query(user_id=uuid4())},
            headers={"Authorization": f"Bearer {create_access_token(user_id=uuid4())}"},
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["sendFriendshipRequest"] == {
            "__typename": "Error",
            "message": error_message,
        }
