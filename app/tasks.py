from uuid import UUID

from asgiref.sync import async_to_sync
from celery import Celery

from app.config import RABBITMQ_URL
from app.domain.repositories.friendship_repository import FriendshipRepository
from app.rabbitmq import get_new_training_queue_name, publish_message

app = Celery("tasks", broker=RABBITMQ_URL)


async def async_handle_new_training(user_id: str, training_id: str):
    async with FriendshipRepository() as repository:
        friends_ids = await repository.get_user_friends_ids(user_id=UUID(user_id))
    for friend_id in friends_ids:
        await publish_message(
            message={
                "training_id": training_id,
            },
            routing_key=get_new_training_queue_name(friend_id),
        )


@app.task
def handle_new_training(user_id: str, training_id: str):
    async_to_sync(async_handle_new_training)(user_id, training_id)
