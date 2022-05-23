import strawberry
from strawberry.types import Info

from app import tasks
from app.database import get_session
from app.domain.repositories import PostgresRepository
from app.graphql.input_types import TrainingInput
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training


async def create_training(info: Info, input: TrainingInput) -> Training:
    user_id = info.context["user_id"]
    async with get_session() as s:
        repository = PostgresRepository(s)
        training = await repository.create_training(
            user_id=user_id,
            name=input.name,
            start_time=input.start_time,
            end_time=input.end_time,
        )
    tasks.handle_new_training.delay(user_id=str(user_id), training_id=str(training.id))
    return Training(
        id=training.id,
        name=training.name,
        start_time=training.start_time,
        end_time=training.end_time,
    )


@strawberry.type
class TrainingMutation:
    create_training: Training = strawberry.mutation(
        resolver=create_training, permission_classes=[IsAuthenticated]
    )
