from uuid import UUID

from strawberry.dataloader import DataLoader

from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql import types as graphql_types


async def get_users_by_ids(keys: list[UUID]) -> list[graphql_types.User]:
    async with get_session() as s:
        repository = PostgresRepository(s)
        return [
            graphql_types.User(id=user.id, email=user.email) if user else None
            for user in await repository.get_users_by_ids(keys)
        ]


get_users_by_ids_loader = DataLoader(load_fn=get_users_by_ids)
