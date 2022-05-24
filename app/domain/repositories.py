from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import coalesce, count

from app import models
from app.domain import entities
from app.domain.exceptions import EmailAlreadyExists
from app.enums import TrainingVisibilityEnum


class PostgresRepository:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def get_user_friends_ids_query(user_id: UUID):
        return select(models.Friendship.user_2_id).where(
            models.Friendship.user_1_id == user_id
        )

    async def get_user_friends_ids(self, user_id: UUID) -> set[UUID]:
        sql = self.get_user_friends_ids_query(user_id)

        results = (await self.session.execute(sql)).all()

        return {result[0] for result in results}

    async def get_training_by_id(self, training_id: UUID) -> entities.Training | None:
        sql = select(models.Training).where(models.Training.id == training_id)
        results = (await self.session.execute(sql)).first()
        if results:
            result = results[0]
            return entities.Training.from_model(result)

    async def get_user_training_by_id(
        self, user_id: UUID, training_id: UUID
    ) -> entities.Training | None:
        sql = select(models.Training).where(
            models.Training.id == training_id, models.Training.user_id == user_id
        )
        results = (await self.session.execute(sql)).first()
        if results:
            result = results[0]
            return entities.Training.from_model(result)

    async def get_user_trainings(
        self, user_id: UUID, request_user_id: UUID
    ) -> list[entities.Training]:
        training_visibility = coalesce(
            models.Training.visibility, models.Profile.training_visibility
        )
        sql = (
            select(models.Training)
            .join(models.User)
            .join(models.Profile)
            .where(
                models.Training.user_id == user_id,
                or_(
                    models.Training.user_id == request_user_id,
                    training_visibility == TrainingVisibilityEnum.public,
                    and_(
                        training_visibility == TrainingVisibilityEnum.only_friends,
                        models.Training.user_id.in_(
                            self.get_user_friends_ids_query(request_user_id)
                        ),
                    ),
                ),
            )
            .order_by(models.Training.start_time.desc())
        )
        trainings = (await self.session.execute(sql)).scalars()
        return [entities.Training.from_model(training) for training in trainings]

    async def create_training(
        self, user_id: UUID, name: str, start_time: datetime, end_time: datetime | None
    ) -> entities.Training:
        training = models.Training(
            user_id=user_id, name=name, start_time=start_time, end_time=end_time
        )
        self.session.add(training)
        await self.session.commit()
        return entities.Training.from_model(training)

    async def create_user(self, email: str, hashed_password: str) -> entities.User:
        user = models.User(email=email, hashed_password=hashed_password)
        profile = models.Profile(user=user)
        self.session.add_all([user, profile])
        try:
            await self.session.commit()
        except IntegrityError:
            raise EmailAlreadyExists()
        return entities.User.from_model(user)

    async def get_reaction_count_by_training_ids(
        self, training_ids: list[UUID]
    ) -> list[int]:
        reactions_query = (
            select(
                models.Reaction.training_id,
            )
            .where(models.Reaction.training_id.in_(training_ids))
            .subquery()
        )
        sql = (
            select(reactions_query.c.training_id, count(reactions_query.c.training_id))
            .group_by(reactions_query.c.training_id)
            .select_from(reactions_query)
        )

        counts = (await self.session.execute(sql)).all()

        counts_dict = {c[0]: c[1] for c in counts}
        return [counts_dict.get(training_id, 0) for training_id in training_ids]

    async def get_reactions_by_training_ids(
        self, training_ids: list[UUID]
    ) -> list[list[entities.Reaction]]:
        sql = (
            select(models.Reaction)
            .where(models.Reaction.training_id.in_(training_ids))
            .order_by(models.Reaction.created_at.desc())
        )

        reactions = (await self.session.execute(sql)).scalars()

        results = defaultdict(list)
        for reaction in reactions:
            results[reaction.training_id].append(entities.Reaction.from_model(reaction))
        return [results.get(training_id, []) for training_id in training_ids]

    async def get_user_by_email(
        self, email: str
    ) -> entities.UserWithHashedPassword | None:
        sql = select(models.User).where(models.User.email == email)

        results = (await self.session.execute(sql)).first()

        if results:
            result = results[0]
            return entities.UserWithHashedPassword.from_model(result)

    async def get_users_by_ids(self, user_ids: list[UUID]) -> list[entities.User]:
        sql = select(models.User).where(models.User.id.in_(user_ids))

        users = (await self.session.execute(sql)).scalars()

        users_by_id = {user.id: entities.User.from_model(user) for user in users}
        return [users_by_id[user_id] for user_id in user_ids]
