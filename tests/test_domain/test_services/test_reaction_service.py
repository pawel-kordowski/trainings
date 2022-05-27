from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.domain.services.reaction_service import ReactionService
from app.enums import ReactionTypeEnum


@patch("app.domain.services.reaction_service.ReactionRepository", autospec=True)
async def test_get_reaction_count_by_training_ids(mocked_repository):
    reaction_count_by_training_ids = [1, 2, 3]
    training_ids = [uuid4(), uuid4(), uuid4()]
    mocked_repository_instance = mocked_repository.return_value.__aenter__.return_value
    mocked_repository_instance.get_reaction_count_by_training_ids.return_value = (
        reaction_count_by_training_ids
    )

    assert (
        await ReactionService.get_reaction_count_by_training_ids(training_ids)
        == reaction_count_by_training_ids
    )
    mocked_repository_instance.get_reaction_count_by_training_ids.assert_awaited_once_with(  # noqa
        training_ids
    )


@patch("app.domain.services.reaction_service.ReactionRepository", autospec=True)
async def test_get_reactions_by_training_ids(mocked_repository):
    reactions_by_training_ids = [
        [
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.like, user_id=uuid4()
            )
        ],
        [],
        [
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.dislike, user_id=uuid4()
            ),
            entities.Reaction(
                id=uuid4(), reaction_type=ReactionTypeEnum.like, user_id=uuid4()
            ),
        ],
    ]
    training_ids = [uuid4(), uuid4(), uuid4()]
    mocked_repository_instance = mocked_repository.return_value.__aenter__.return_value
    mocked_repository_instance.get_reactions_by_training_ids.return_value = (
        reactions_by_training_ids
    )

    assert (
        await ReactionService.get_reactions_by_training_ids(training_ids)
        == reactions_by_training_ids
    )
    mocked_repository_instance.get_reactions_by_training_ids.assert_awaited_once_with(
        training_ids
    )
