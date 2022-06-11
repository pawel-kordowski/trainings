from uuid import UUID

from sqlalchemy import and_, or_, select

from app import enums, models
from app.domain import entities
from app.domain.repositories.base import PostgresRepository


class FriendshipRequestRepository(PostgresRepository):
    async def update_status(
        self, friendship_request_id: UUID, status: enums.FriendshipRequestStatusEnum
    ):
        pass

    async def get_request_by_id(
        self, friendship_request_id: UUID
    ) -> entities.FriendshipRequest | None:
        sql = select(models.FriendshipRequest).where(
            models.FriendshipRequest.id == friendship_request_id
        )

        results = (await self.session.execute(sql)).scalar()

        if results:
            return entities.FriendshipRequest.from_model(results[0])

    async def does_pending_request_exist(
        self, user_1_id: UUID, user_2_id: UUID
    ) -> bool:
        sql = self._get_pending_requests_query().where(
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

    def _get_pending_requests_query(self):
        return (
            select(models.FriendshipRequest)
            .where(
                models.FriendshipRequest.status
                == enums.FriendshipRequestStatusEnum.pending,
            )
            .order_by(models.FriendshipRequest.timestamp)
        )

    async def get_pending_requests_received_by_user(
        self, user_id: UUID
    ) -> list[entities.FriendshipRequest]:
        sql = self._get_pending_requests_query().where(
            models.FriendshipRequest.receiver_id == user_id
        )

        friendship_requests = (await self.session.execute(sql)).scalars()

        return [
            entities.FriendshipRequest.from_model(friendship_request)
            for friendship_request in friendship_requests
        ]

    async def get_pending_requests_sent_by_user(
        self, user_id: UUID
    ) -> list[entities.FriendshipRequest]:
        sql = self._get_pending_requests_query().where(
            models.FriendshipRequest.sender_id == user_id
        )

        friendship_requests = (await self.session.execute(sql)).scalars()

        return [
            entities.FriendshipRequest.from_model(friendship_request)
            for friendship_request in friendship_requests
        ]
