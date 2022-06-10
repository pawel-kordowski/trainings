from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app import models
from app.domain import entities
from app.domain.exceptions import EmailAlreadyExists
from app.domain.repositories.base import PostgresRepository


class UserRepository(PostgresRepository):
    async def create_user(self, email: str, hashed_password: str) -> entities.User:
        user = models.User(email=email, hashed_password=hashed_password)
        profile = models.Profile(user=user)
        self.session.add_all([user, profile])
        try:
            await self.session.commit()
        except IntegrityError:
            raise EmailAlreadyExists()
        return entities.User.from_model(user)

    async def get_user_by_email(
        self, email: str
    ) -> entities.UserWithHashedPassword | None:
        sql = select(models.User).where(models.User.email == email)

        results = (await self.session.execute(sql)).first()

        if results:
            result = results[0]
            return entities.UserWithHashedPassword.from_model(result)

    async def does_user_with_id_exist(self, user_id: UUID) -> bool:
        sql = select(models.User).where(models.User.id == user_id)

        results = (await self.session.execute(sql)).first()

        return bool(results)

    async def get_users_by_ids(self, user_ids: list[UUID]) -> list[entities.User]:
        sql = select(models.User).where(models.User.id.in_(user_ids))

        users = (await self.session.execute(sql)).scalars()

        users_by_id = {user.id: entities.User.from_model(user) for user in users}
        return [users_by_id[user_id] for user_id in user_ids]
