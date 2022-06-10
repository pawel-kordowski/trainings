from unittest.mock import patch
from uuid import uuid4

from app import enums, helpers
from app.domain.entities import FriendshipRequest, User
from app.jwt_tokens import create_access_token


class TestMySentFriendshipRequests:
    query = """
    {
        mySentFriendshipRequests{
            id
            senderId
            receiverId
            timestamp
            sender{
                id
                email
            }
            receiver{
                id
                email
            }
        }
    }
    """

    def test_requires_authorization(self, client):
        response = client.post("/graphql", json={"query": self.query})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"] is None
        assert response_json["errors"][0]["message"] == "User is not authenticated"

    @patch(
        "app.graphql.queries.friendship_requests.FriendshipRequestService",
        autospec=True,
    )
    @patch("app.graphql.data_loaders.users.UserService", autospec=True)
    def test_successful(
        self, mocked_user_service, mocked_friendship_request_service, client
    ):
        user_1 = User(id=uuid4(), email="user_1@test.com")
        user_2 = User(id=uuid4(), email="user_2@test.com")
        user_3 = User(id=uuid4(), email="user_3@test.com")
        friendship_request_1 = FriendshipRequest(
            id=uuid4(),
            sender_id=user_1.id,
            receiver_id=user_2.id,
            status=enums.FriendshipRequestStatusEnum.pending,
            timestamp=helpers.get_utc_now(),
        )
        friendship_request_2 = FriendshipRequest(
            id=uuid4(),
            sender_id=user_1.id,
            receiver_id=user_3.id,
            status=enums.FriendshipRequestStatusEnum.pending,
            timestamp=helpers.get_utc_now(),
        )
        friendship_requests = [friendship_request_1, friendship_request_2]
        receiver_by_friendship_request_id = {
            friendship_request_1.id: user_2,
            friendship_request_2.id: user_3,
        }
        mocked_friendship_request_service.get_pending_requests_sent_by_user.return_value = (  # noqa
            friendship_requests
        )
        mocked_user_service.get_users_by_ids.return_value = [user_1, user_2, user_3]

        response = client.post(
            "/graphql",
            json={"query": self.query},
            headers={"Authorization": f"Bearer {create_access_token(user_1.id)}"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["mySentFriendshipRequests"] == [
            {
                "id": str(friendship_request.id),
                "senderId": str(friendship_request.sender_id),
                "receiverId": str(friendship_request.receiver_id),
                "timestamp": friendship_request.timestamp.isoformat(),
                "receiver": {
                    "id": str(
                        receiver_by_friendship_request_id[friendship_request.id].id
                    ),
                    "email": receiver_by_friendship_request_id[
                        friendship_request.id
                    ].email,
                },
                "sender": {"id": str(user_1.id), "email": user_1.email},
            }
            for friendship_request in friendship_requests
        ]
        mocked_friendship_request_service.get_pending_requests_sent_by_user.assert_awaited_once_with(  # noqa
            user_id=user_1.id
        )
        mocked_user_service.get_users_by_ids.assert_awaited_once_with(
            [user_1.id, user_2.id, user_3.id]
        )
