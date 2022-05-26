from datetime import datetime
from uuid import UUID

from app import tasks
from app.domain import entities
from app.domain.repositories.training_repository import TrainingRepository


class TrainingService:
    @staticmethod
    async def create_training(
        user_id: UUID, name: str, start_time: datetime, end_time: datetime
    ) -> entities.Training:
        async with TrainingRepository() as repository:
            training = await repository.create_training(
                user_id=user_id,
                name=name,
                start_time=start_time,
                end_time=end_time,
            )
        tasks.handle_new_training.delay(
            user_id=str(user_id), training_id=str(training.id)
        )
        return training

    @staticmethod
    async def get_training(
        request_user_id: UUID, training_id: UUID
    ) -> entities.Training | None:
        async with TrainingRepository() as repository:
            return await repository.get_training_by_id(
                request_user_id=request_user_id, training_id=training_id
            )

    @staticmethod
    async def get_user_trainings(
        request_user_id: UUID, user_id: UUID
    ) -> list[entities.Training]:
        async with TrainingRepository() as repository:
            return await repository.get_user_trainings(
                request_user_id=request_user_id, user_id=user_id
            )
