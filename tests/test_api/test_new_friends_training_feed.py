from datetime import datetime

from app.jwt_tokens import create_access_token
from tests.factories import FriendshipFactory


def test_new_friends_training_feed(client, db_session):
    friendship = FriendshipFactory()
    query = """
    subscription {
        newFriendsTrainingFeed {
            id
            name
            startTime
            endTime
        }
    }
    """
    name = "New training"
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    create_training_query = f"""
    mutation {{
        createTraining(
            input:{{
                name: "{name}"
                startTime: "{start_time.isoformat()}"
                endTime: "{end_time.isoformat()}"
            }}
        ) {{
            id
        }}
    }}
    """
    with client.websocket_connect(
        f"/graphql?auth={create_access_token(friendship.user_2.id)}",
        subprotocols=["graphql-ws"],
    ) as websocket:
        websocket.send_json(
            {
                "id": 1,
                "type": "start",
                "payload": {"query": query},
            }
        )
        response = client.post(
            "/graphql",
            json={
                "query": create_training_query,
            },
            headers={
                "Authorization": f"Bearer {create_access_token(friendship.user_1.id)}"
            },
        )
        training_id = response.json()["data"]["createTraining"]["id"]
        data = websocket.receive_json()
        assert data["payload"]["data"]["newFriendsTrainingFeed"] == {
            "id": training_id,
            "name": name,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
        }
