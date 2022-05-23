from uuid import UUID

import strawberry

from app import enums
from app.graphql.types.users import User

ReactionTypeEnum = strawberry.enum(enums.ReactionTypeEnum)


@strawberry.type
class Reaction:
    id: UUID
    reaction_type: ReactionTypeEnum
    user_id: UUID

    @strawberry.field
    async def user(self) -> User:
        from app.graphql.data_loaders.users import get_users_by_ids_loader

        return await get_users_by_ids_loader.load(self.user_id)
