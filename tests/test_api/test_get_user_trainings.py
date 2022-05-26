from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.enums import ReactionTypeEnum
from app.jwt_tokens import create_access_token


def test_query_trainings_requires_authorization(client):
    query = f"""
    {{
        trainings(userId: "{uuid4()}"){{
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
    assert response_json["data"] is None
    assert response_json["errors"][0]["message"] == "User is not authenticated"


@patch("app.graphql.queries.trainings.TrainingService", autospec=True)
@patch("app.graphql.data_loaders.reactions.ReactionService", autospec=True)
@patch("app.graphql.data_loaders.users.UserService", autospec=True)
def test_query_user_trainings(
    mocked_user_service, mocked_reaction_service, mocked_training_service, client
):
    request_user_id = uuid4()
    user_id = uuid4()
    user_1_id = uuid4()
    user_2_id = uuid4()
    trainings = [
        entities.Training(
            id=uuid4(),
            name="Training 1",
            start_time=datetime.fromisoformat("2020-10-10T10:00:00"),
            end_time=datetime.fromisoformat("2020-10-10T11:00:00"),
            user_id=user_id,
        ),
        entities.Training(
            id=uuid4(),
            name="Training 2",
            start_time=datetime.fromisoformat("2020-10-10T12:00:00"),
            end_time=datetime.fromisoformat("2020-10-10T13:00:00"),
            user_id=user_id,
        ),
    ]
    mocked_training_service.get_user_trainings.return_value = trainings
    reactions_count_by_training_id = {trainings[0].id: 0, trainings[1].id: 5}
    mocked_reaction_service.get_reaction_count_by_training_ids.return_value = list(
        reactions_count_by_training_id.values()
    )
    reactions_by_training_id = {
        trainings[0].id: [
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.like, user_id=user_1_id
            ),
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.dislike, user_id=user_2_id
            ),
        ],
        trainings[1].id: [
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.like, user_id=user_1_id
            ),
        ],
    }
    mocked_reaction_service.get_reactions_by_training_ids.return_value = list(
        reactions_by_training_id.values()
    )
    users_by_id = {
        user_1_id: entities.User(id=user_1_id, email="user_1@test.com"),
        user_2_id: entities.User(id=user_2_id, email="user_2@test.com"),
    }
    mocked_user_service.get_users_by_ids.return_value = list(users_by_id.values())

    query = f"""
    {{
        trainings(userId: "{user_id}"){{
            id
            name
            startTime
            endTime
            reactionsCount
            reactions{{
                id
                reactionType
                user{{
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
        headers={"Authorization": f"Bearer {create_access_token(request_user_id)}"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["trainings"] == [
        {
            "id": str(training.id),
            "name": training.name,
            "startTime": training.start_time.isoformat(),
            "endTime": training.end_time.isoformat(),
            "reactionsCount": reactions_count_by_training_id[training.id],
            "reactions": [
                {
                    "id": str(reaction.id),
                    "reactionType": str(reaction.reaction_type.value),
                    "user": {
                        "id": str(users_by_id[reaction.user_id].id),
                        "email": users_by_id[reaction.user_id].email,
                    },
                }
                for reaction in reactions_by_training_id[training.id]
            ],
        }
        for training in trainings
    ]

    training_ids = [training.id for training in trainings]
    mocked_training_service.get_user_trainings.assert_awaited_once_with(
        request_user_id=request_user_id, user_id=user_id
    )
    mocked_reaction_service.get_reaction_count_by_training_ids.assert_awaited_once_with(
        keys=training_ids
    )
    mocked_reaction_service.get_reactions_by_training_ids.assert_awaited_once_with(
        keys=training_ids
    )
    mocked_user_service.get_users_by_ids.assert_awaited_once_with(
        list(users_by_id.keys())
    )
