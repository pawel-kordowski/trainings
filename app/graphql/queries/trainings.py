from uuid import UUID

import strawberry
from strawberry.types import Info

from app.domain.services.training_service import TrainingService
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Training


async def get_training(info: Info, id: UUID) -> Training | None:
    training = await TrainingService.get_training(
        request_user_id=info.context["user_id"],
        training_id=id,
    )
    if training:
        return Training.from_entity(training)


async def get_user_trainings(info: Info, user_id: UUID) -> list[Training]:
    trainings = await TrainingService.get_user_trainings(
        request_user_id=info.context["user_id"], user_id=user_id
    )
    return [Training.from_entity(training) for training in trainings]


@strawberry.type
class TrainingQuery:
    training: Training | None = strawberry.field(
        resolver=get_training, permission_classes=[IsAuthenticated]
    )
    trainings: list[Training] = strawberry.field(
        resolver=get_user_trainings, permission_classes=[IsAuthenticated]
    )
