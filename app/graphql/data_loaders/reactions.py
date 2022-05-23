from uuid import UUID

from strawberry.dataloader import DataLoader

from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql import types as graphql_types


async def get_reaction_count_by_training_ids(keys: list[UUID]) -> list[int]:
    async with get_session() as s:
        repository = PostgresRepository(s)
        return await repository.get_reaction_count_by_training_ids(keys)


get_reaction_count_by_training_ids_loader = DataLoader(
    load_fn=get_reaction_count_by_training_ids
)


async def get_reactions_by_training_ids(
    keys: list[UUID],
) -> list[list[graphql_types.Reaction]]:
    async with get_session() as s:
        repository = PostgresRepository(s)
        return [
            [
                graphql_types.Reaction(
                    id=reaction.id,
                    reaction_type=graphql_types.ReactionTypeEnum(
                        reaction.reaction_type
                    ),
                    user_id=reaction.user_id,
                )
                for reaction in reactions
            ]
            for reactions in await repository.get_reactions_by_training_ids(keys)
        ]


get_reactions_by_training_ids_loader = DataLoader(load_fn=get_reactions_by_training_ids)
