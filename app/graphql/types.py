from datetime import datetime
from uuid import UUID

import strawberry

from app import enums

ReactionTypeEnum = strawberry.enum(enums.ReactionTypeEnum)


@strawberry.type
class User:
    id: UUID
    email: str


@strawberry.type
class Reaction:
    id: UUID
    reaction_type: ReactionTypeEnum
    user_id: UUID

    @strawberry.field
    async def user(self) -> User:
        from app.graphql.data_loaders import get_users_by_ids_loader

        return await get_users_by_ids_loader.load(self.user_id)


@strawberry.type
class Training:
    id: UUID
    start_time: datetime
    end_time: datetime | None
    name: str

    @strawberry.field
    async def reactions_count(self) -> int:
        from app.graphql.data_loaders import get_reaction_count_by_training_ids_loader

        return await get_reaction_count_by_training_ids_loader.load(self.id)

    @strawberry.field
    async def reactions(self) -> list[Reaction]:
        from app.graphql.data_loaders import get_reactions_by_training_ids_loader

        return await get_reactions_by_training_ids_loader.load(self.id)
