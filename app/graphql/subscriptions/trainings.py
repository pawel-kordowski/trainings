from typing import AsyncGenerator
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training
from app.rabbitmq import get_message, get_new_training_queue_name


async def get_new_friends_training(info: Info):
    async for message in get_message(
        get_new_training_queue_name(info.context["user_id"])
    ):
        async with get_session() as s:
            repository = PostgresRepository(s)
            training = await repository.get_training_by_id(UUID(message["training_id"]))
        if training:
            yield Training(
                id=training.id,
                name=training.name,
                start_time=training.start_time,
                end_time=training.end_time,
            )


@strawberry.type
class TrainingSubscription:
    new_friends_training_feed: AsyncGenerator[Training, None] = strawberry.subscription(
        resolver=get_new_friends_training, permission_classes=[IsAuthenticated]
    )
