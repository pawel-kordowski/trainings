from datetime import datetime, timedelta
from uuid import uuid4

from app.database import engine
from app.domain import entities
from app.domain.repositories.reaction_repository import ReactionRepository
from tests.test_domain.test_repositories.factories import (
    TrainingFactory,
    ReactionFactory,
)
from tests.test_domain.test_repositories.sqlalchemy_helpers import QueryCounter


async def test_get_reaction_count_by_training_ids(db_session):
    training_1 = TrainingFactory()
    ReactionFactory.create_batch(10, training=training_1)
    training_2 = TrainingFactory()
    training_3 = TrainingFactory()
    ReactionFactory.create_batch(5, training=training_3)

    async with ReactionRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_reaction_count_by_training_ids(
                [training_1.id, training_2.id, training_3.id, uuid4()]
            ) == [10, 0, 5, 0]
        assert query_counter.count == 1


async def test_get_reactions_by_training_ids(db_session):
    training_1 = TrainingFactory()
    created_at_base = datetime.fromisoformat("2020-10-10T10:00:00")
    training_1_reaction_1 = ReactionFactory(
        training=training_1, created_at=created_at_base
    )
    training_1_reaction_2 = ReactionFactory(
        training=training_1, created_at=created_at_base - timedelta(minutes=1)
    )
    training_1_reaction_3 = ReactionFactory(
        training=training_1, created_at=created_at_base + timedelta(minutes=1)
    )
    training_1_reactions = [
        training_1_reaction_3,
        training_1_reaction_1,
        training_1_reaction_2,
    ]
    training_2 = TrainingFactory()
    training_3 = TrainingFactory()
    training_3_reaction = ReactionFactory(training=training_3)

    async with ReactionRepository() as repository:
        with QueryCounter(engine.sync_engine) as query_counter:
            assert await repository.get_reactions_by_training_ids(
                [training_1.id, training_2.id, training_3.id, uuid4()]
            ) == [
                [
                    entities.Reaction(
                        id=reaction.id,
                        reaction_type=reaction.reaction_type,
                        user_id=reaction.user_id,
                    )
                    for reaction in training_1_reactions
                ],
                [],
                [
                    entities.Reaction(
                        id=training_3_reaction.id,
                        reaction_type=training_3_reaction.reaction_type,
                        user_id=training_3_reaction.user_id,
                    )
                ],
                [],
            ]
        assert query_counter.count == 1
