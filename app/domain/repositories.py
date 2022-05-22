from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.sql.functions import count

from app import models
from app.domain import entities


class PostgresRepository:
    def __init__(self, session):
        self.session = session

    async def get_user_friends_ids(self, user_id: UUID) -> set[UUID]:
        sql = select(models.Friendship.user_2_id).where(models.Friendship.user_1_id == user_id)

        results = (await self.session.execute(sql)).all()

        return {result[0] for result in results}

    async def get_training_by_id(
        self, training_id: UUID
    ) -> entities.Training | None:
        sql = select(models.Training).where(
            models.Training.id == training_id
        )
        results = (await self.session.execute(sql)).first()
        if results:
            result = results[0]
            return entities.Training(
                id=result.id,
                start_time=result.start_time,
                end_time=result.end_time,
                name=result.name,
                user_id=result.user_id,
            )

    async def get_user_training_by_id(
        self, user_id: UUID, training_id: UUID
    ) -> entities.Training | None:
        sql = select(models.Training).where(
            models.Training.id == training_id, models.Training.user_id == user_id
        )
        results = (await self.session.execute(sql)).first()
        if results:
            result = results[0]
            return entities.Training(
                id=result.id,
                start_time=result.start_time,
                end_time=result.end_time,
                name=result.name,
                user_id=result.user_id,
            )

    async def get_user_trainings(self, user_id: UUID) -> list[entities.Training]:
        sql = (
            select(models.Training)
            .where(models.Training.user_id == user_id)
            .order_by(models.Training.start_time.desc())
        )
        trainings = (await self.session.execute(sql)).scalars()
        return [
            entities.Training(
                id=training.id,
                start_time=training.start_time,
                end_time=training.end_time,
                name=training.name,
                user_id=training.user_id,
            )
            for training in trainings
        ]

    async def create_training(
        self, user_id: UUID, name: str, start_time: datetime, end_time: datetime | None
    ) -> entities.Training:
        training = models.Training(
            user_id=user_id, name=name, start_time=start_time, end_time=end_time
        )
        self.session.add(training)
        await self.session.commit()
        return entities.Training(
            id=training.id,
            start_time=training.start_time,
            end_time=training.end_time,
            name=training.name,
            user_id=training.user_id,
        )

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
            results[reaction.training_id].append(
                entities.Reaction(
                    id=reaction.id,
                    reaction_type=reaction.reaction_type,
                    user_id=reaction.user_id,
                )
            )
        return [results.get(training_id, []) for training_id in training_ids]

    async def get_users_by_ids(self, user_ids: list[UUID]) -> list[entities.User]:
        sql = select(models.User).where(models.User.id.in_(user_ids))

        users = (await self.session.execute(sql)).scalars()

        users_by_id = {
            user.id: entities.User(id=user.id, email=user.email) for user in users
        }
        return [users_by_id[user_id] for user_id in user_ids]
