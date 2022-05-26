from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.enums import ReactionTypeEnum
from app.jwt_tokens import create_access_token


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


@patch("app.graphql.queries.trainings.TrainingService", autospec=True)
@patch("app.graphql.data_loaders.reactions.ReactionService", autospec=True)
@patch("app.graphql.data_loaders.users.UserService", autospec=True)
def test_query_existing_training(
    mocked_user_service, mocked_reaction_service, mocked_training_service, client
):
    user_id = uuid4()
    training_id = uuid4()
    start_time = datetime.fromisoformat("2020-10-10T10:00:00")
    end_time = datetime.fromisoformat("2020-10-10T11:00:00")
    name = "name"
    mocked_training_service.get_training.return_value = entities.Training(
        id=training_id,
        name=name,
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
    )
    reactions_count = 5
    mocked_reaction_service.get_reaction_count_by_training_ids.return_value = [
        reactions_count
    ]
    user_1_id = uuid4()
    user_2_id = uuid4()
    reactions = [
        entities.Reaction(
            id=uuid4(), reaction_type=ReactionTypeEnum.like, user_id=user_1_id
        ),
        entities.Reaction(
            id=uuid4(), reaction_type=ReactionTypeEnum.dislike, user_id=user_2_id
        ),
    ]
    mocked_reaction_service.get_reactions_by_training_ids.return_value = [reactions]
    users_by_id = {
        user_1_id: entities.User(id=user_1_id, email="user_1@test.com"),
        user_2_id: entities.User(id=user_2_id, email="user_2@test.com"),
    }
    mocked_user_service.get_users_by_ids.return_value = list(users_by_id.values())

    query = f"""
    {{
        training(id: "{training_id}"){{
            id
            startTime
            endTime
            name
            reactionsCount
            reactions{{
                id
                reactionType
                user {{
                    id
                    email
                }}
            }}
        }}
    }}
    """

    response = client.post(
        "/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {create_access_token(user_id)}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["training"] == {
        "id": str(training_id),
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "name": name,
        "reactionsCount": reactions_count,
        "reactions": [
            {
                "id": str(reaction.id),
                "reactionType": str(reaction.reaction_type.value),
                "user": {
                    "id": str(reaction.user_id),
                    "email": users_by_id[reaction.user_id].email,
                },
            }
            for reaction in reactions
        ],
    }

    mocked_training_service.get_training.assert_awaited_once_with(
        request_user_id=user_id, training_id=training_id
    )
    mocked_reaction_service.get_reaction_count_by_training_ids.assert_awaited_once_with(
        keys=[training_id]
    )
    mocked_reaction_service.get_reactions_by_training_ids.assert_awaited_once_with(
        keys=[training_id]
    )
    mocked_user_service.get_users_by_ids.assert_awaited_once_with(
        list(users_by_id.keys())
    )
