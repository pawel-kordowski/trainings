from uuid import UUID

from sqlalchemy import and_, or_, select

from app import enums, models
from app.domain import entities
from app.domain.repositories.base import PostgresRepository


class FriendshipRequestRepository(PostgresRepository):
    async def does_pending_request_exists(
        self, user_1_id: UUID, user_2_id: UUID
    ) -> bool:
        sql = select(models.FriendshipRequest).where(
            models.FriendshipRequest.status
            == enums.FriendshipRequestStatusEnum.pending,
            or_(
                and_(
                    models.FriendshipRequest.sender_id == user_1_id,
                    models.FriendshipRequest.receiver_id == user_2_id,
                ),
                and_(
                    models.FriendshipRequest.sender_id == user_2_id,
                    models.FriendshipRequest.receiver_id == user_1_id,
                ),
            ),
        )

        results = (await self.session.execute(sql)).first()

        return bool(results)

    async def create_pending_request(
        self, sender_id: UUID, receiver_id: UUID
    ) -> entities.FriendshipRequest:
        friendship_request = models.FriendshipRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=enums.FriendshipRequestStatusEnum.pending,
        )
        self.session.add(friendship_request)
        await self.session.commit()
        return entities.FriendshipRequest.from_model(friendship_request)
