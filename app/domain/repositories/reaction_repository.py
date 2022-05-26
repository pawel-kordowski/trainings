from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.sql.functions import count

from app import models
from app.domain import entities
from app.domain.repositories.base import PostgresRepository


class ReactionRepository(PostgresRepository):
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
