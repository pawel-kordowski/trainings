from uuid import UUID

from strawberry.dataloader import DataLoader

from app.domain.services.reaction_service import ReactionService
from app.graphql import types as graphql_types


async def get_reaction_count_by_training_ids(keys: list[UUID]) -> list[int]:
    return await ReactionService.get_reaction_count_by_training_ids(keys)


get_reaction_count_by_training_ids_loader = DataLoader(
    load_fn=get_reaction_count_by_training_ids
)


async def get_reactions_by_training_ids(
    keys: list[UUID],
) -> list[list[graphql_types.Reaction]]:
    return [
        [graphql_types.Reaction.from_entity(reaction) for reaction in reactions]
        for reactions in await ReactionService.get_reactions_by_training_ids(keys)
    ]


get_reactions_by_training_ids_loader = DataLoader(load_fn=get_reactions_by_training_ids)
