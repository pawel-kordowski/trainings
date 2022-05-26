from uuid import UUID

from sqlalchemy import select

from app import models
from app.domain.repositories.base import PostgresRepository


class FriendshipRepository(PostgresRepository):
    @staticmethod
    def get_user_friends_ids_query(user_id: UUID):
        return select(models.Friendship.user_2_id).where(
            models.Friendship.user_1_id == user_id
        )

    async def get_user_friends_ids(self, user_id: UUID) -> set[UUID]:
        sql = self.get_user_friends_ids_query(user_id)

        results = (await self.session.execute(sql)).all()

        return {result[0] for result in results}
