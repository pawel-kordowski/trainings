from typing import List, Optional
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training


async def get_training(info: Info, id: UUID) -> Optional[Training]:
    async with get_session() as s:
        repository = PostgresRepository(s)
        training = await repository.get_user_training_by_id(info.context["user_id"], id)
    if training:
        return Training(
            id=training.id,
            start_time=training.start_time,
            end_time=training.end_time,
            name=training.name,
        )


async def get_user_trainings(info: Info) -> List[Training]:
    async with get_session() as s:
        repository = PostgresRepository(s)
        trainings = await repository.get_user_trainings(info.context["user_id"])
    return [
        Training(
            id=training.id,
            start_time=training.start_time,
            end_time=training.end_time,
            name=training.name,
        )
        for training in trainings
    ]


@strawberry.type
class Query:
    training: Optional[Training] = strawberry.field(
        resolver=get_training, permission_classes=[IsAuthenticated]
    )
    trainings: List[Training] = strawberry.field(
        resolver=get_user_trainings, permission_classes=[IsAuthenticated]
    )
