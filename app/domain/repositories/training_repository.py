from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.sql.functions import coalesce

from app import models
from app.domain import entities
from app.domain.repositories.base import PostgresRepository
from app.domain.repositories.friendship_repository import FriendshipRepository
from app.enums import TrainingVisibilityEnum


class TrainingRepository(PostgresRepository):
    async def get_training_by_id(
        self, request_user_id: UUID, training_id: UUID
    ) -> entities.Training | None:
        sql = self.get_visible_trainings_for_user_query(request_user_id).where(
            models.Training.id == training_id
        )
        results = (await self.session.execute(sql)).first()
        if results:
            result = results[0]
            return entities.Training.from_model(result)

    async def get_user_trainings(
        self, request_user_id: UUID, user_id: UUID
    ) -> list[entities.Training]:
        sql = self.get_visible_trainings_for_user_query(request_user_id).where(
            models.Training.user_id == user_id
        )
        trainings = (await self.session.execute(sql)).scalars()
        return [entities.Training.from_model(training) for training in trainings]

    def get_visible_trainings_for_user_query(self, user_id):
        training_visibility = coalesce(
            models.Training.visibility, models.Profile.training_visibility
        )
        return (
            select(models.Training)
            .join(models.User)
            .join(models.Profile)
            .where(
                or_(
                    models.Training.user_id == user_id,
                    training_visibility == TrainingVisibilityEnum.public,
                    and_(
                        training_visibility == TrainingVisibilityEnum.only_friends,
                        models.Training.user_id.in_(
                            FriendshipRepository.get_user_friends_ids_query(user_id)
                        ),
                    ),
                ),
            )
            .order_by(models.Training.start_time.desc())
        )

    async def create_training(
        self, user_id: UUID, name: str, start_time: datetime, end_time: datetime | None
    ) -> entities.Training:
        training = models.Training(
            user_id=user_id, name=name, start_time=start_time, end_time=end_time
        )
        self.session.add(training)
        await self.session.commit()
        return entities.Training.from_model(training)
