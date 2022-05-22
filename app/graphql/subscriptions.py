from datetime import datetime
from typing import AsyncGenerator

import strawberry

from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training
from app.rabbitmq import get_message


async def get_new_friends_training():
    async for message in get_message("test_queue"):
        yield Training(
            id=message["id"],
            name=message["name"],
            start_time=datetime.fromisoformat(message["start_time"]),
            end_time=datetime.fromisoformat(message["end_time"]),
        )


@strawberry.type
class Subscription:
    new_friends_training_feed: AsyncGenerator[Training, None] = strawberry.subscription(
        resolver=get_new_friends_training, permission_classes=[IsAuthenticated]
    )
