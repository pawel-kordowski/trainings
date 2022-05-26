from uuid import UUID

from strawberry.dataloader import DataLoader

from app.domain.services.user_service import UserService
from app.graphql import types as graphql_types


async def get_users_by_ids(keys: list[UUID]) -> list[graphql_types.User]:
    return [
        graphql_types.User.from_entity(user) if user else None
        for user in await UserService.get_users_by_ids(keys)
    ]


get_users_by_ids_loader = DataLoader(load_fn=get_users_by_ids)
