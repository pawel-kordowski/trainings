import strawberry
from strawberry.types import Info

from app.domain.services.training_service import TrainingService
from app.graphql.input_types import TrainingInput
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training


async def create_training(info: Info, input: TrainingInput) -> Training:
    training = await TrainingService.create_training(
        user_id=info.context["user_id"],
        name=input.name,
        start_time=input.start_time,
        end_time=input.end_time,
    )
    return Training.from_entity(training)


@strawberry.type
class TrainingMutation:
    create_training: Training = strawberry.mutation(
        resolver=create_training, permission_classes=[IsAuthenticated]
    )
