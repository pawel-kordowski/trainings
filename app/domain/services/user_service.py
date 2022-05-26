from uuid import UUID

from app.domain import entities
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.exceptions import LoginFailed
from app.jwt_tokens import create_access_token
from app.passwords import get_password_hash, verify_password


class UserService:
    @staticmethod
    async def get_users_by_ids(keys: list[UUID]) -> list[entities.User]:
        async with UserRepository() as repository:
            return await repository.get_users_by_ids(keys)

    @staticmethod
    async def create_user(email: str, password: str) -> entities.User:
        hashed_password = get_password_hash(password)
        async with UserRepository() as repository:
            return await repository.create_user(
                email=email, hashed_password=hashed_password
            )

    @staticmethod
    async def get_user_jwt(email: str, password: str) -> str:
        async with UserRepository() as repository:
            user = await repository.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise LoginFailed()
        return create_access_token(user.id)
