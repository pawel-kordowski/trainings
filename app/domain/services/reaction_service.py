from uuid import UUID

from app.domain import entities
from app.domain.repositories.reaction_repository import ReactionRepository


class ReactionService:
    @staticmethod
    async def get_reaction_count_by_training_ids(keys: list[UUID]) -> list[int]:
        async with ReactionRepository() as repository:
            return await repository.get_reaction_count_by_training_ids(keys)

    @staticmethod
    async def get_reactions_by_training_ids(
        keys: list[UUID],
    ) -> list[list[entities.Reaction]]:
        async with ReactionRepository() as repository:
            return await repository.get_reactions_by_training_ids(keys)
