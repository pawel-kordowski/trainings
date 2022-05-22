from datetime import datetime

from app.jwt_tokens import create_access_token


def test_new_friends_training_feed(client, user):
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
        "/graphql",
        subprotocols=["graphql-ws"],
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    ) as websocket:
        websocket.send_json(
            {
                "id": 1,
                "type": "start",
                "payload": {"query": query},
            }
        )
        client.post(
            "/graphql",
            json={
                "query": create_training_query,
            },
            headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
        )
        websocket.receive_json()
