from typing import AsyncGenerator
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.domain.repositories.training_repository import TrainingRepository
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training
from app.rabbitmq import get_message, get_new_training_queue_name


async def get_new_friends_training(info: Info):
    user_id = info.context["user_id"]
    async for message in get_message(get_new_training_queue_name(user_id)):
        async with TrainingRepository() as repository:
            training = await repository.get_training_by_id(
                request_user_id=user_id, training_id=UUID(message["training_id"])
            )
        if training:
            yield Training.from_entity(training)


@strawberry.type
class TrainingSubscription:
    new_friends_training_feed: AsyncGenerator[Training, None] = strawberry.subscription(
        resolver=get_new_friends_training, permission_classes=[IsAuthenticated]
    )
