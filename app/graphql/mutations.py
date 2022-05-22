import strawberry
from strawberry.types import Info

from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql.input_types import TrainingInput
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training
from app.rabbitmq import publish_message


async def create_training(info: Info, input: TrainingInput) -> Training:
    async with get_session() as s:
        repository = PostgresRepository(s)
        training = await repository.create_training(
            user_id=info.context["user_id"],
            name=input.name,
            start_time=input.start_time,
            end_time=input.end_time,
        )
    await publish_message(
        {
            "id": str(training.id),
            "name": training.name,
            "start_time": training.start_time.isoformat(),
            "end_time": training.end_time.isoformat(),
        },
        "test_queue",
    )
    return Training(
        id=training.id,
        name=training.name,
        start_time=training.start_time,
        end_time=training.end_time,
    )


@strawberry.type
class Mutation:
    create_training: Training = strawberry.mutation(
        resolver=create_training, permission_classes=[IsAuthenticated]
    )
