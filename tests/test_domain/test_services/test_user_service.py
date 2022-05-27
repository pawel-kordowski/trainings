from unittest.mock import patch
from uuid import uuid4

import pytest

from app.domain import entities
from app.domain.services.exceptions import LoginFailed
from app.domain.services.user_service import UserService


@patch("app.domain.services.user_service.UserRepository")
async def test_get_users_by_ids(mocked_user_repository):
    user_ids = [uuid4(), uuid4()]
    users = [
        entities.User(id=uuid4(), email="test@test@com"),
        entities.User(id=uuid4(), email="test_1@test.com"),
    ]
    mocked_user_repository_instance = (
        mocked_user_repository.return_value.__aenter__.return_value
    )
    mocked_user_repository_instance.get_users_by_ids.return_value = users

    assert await UserService.get_users_by_ids(user_ids) == users
    mocked_user_repository_instance.get_users_by_ids.assert_awaited_once_with(user_ids)


@patch("app.domain.services.user_service.UserRepository")
@patch("app.domain.services.user_service.get_password_hash")
async def test_create_user(mocked_get_password_hash, mocked_user_repository):
    email = "test@test.com"
    password = "password"
    hashed_password = "hashed_password"
    user = entities.User(id=uuid4(), email=email)
    mocked_user_repository_instance = (
        mocked_user_repository.return_value.__aenter__.return_value
    )
    mocked_user_repository_instance.create_user.return_value = user
    mocked_get_password_hash.return_value = hashed_password

    assert await UserService.create_user(email=email, password=password) == user
    mocked_user_repository_instance.create_user.assert_awaited_once_with(
        email=email, hashed_password=hashed_password
    )


@patch("app.domain.services.user_service.UserRepository")
async def test_create_user_no_user(mocked_user_repository):
    email = "test@test.com"
    mocked_user_repository_instance = (
        mocked_user_repository.return_value.__aenter__.return_value
    )
    mocked_user_repository_instance.get_user_by_email.return_value = None

    with pytest.raises(LoginFailed):
        assert await UserService.get_user_jwt(email=email, password="password")
    mocked_user_repository_instance.get_user_by_email.assert_awaited_once_with(email)


@patch("app.domain.services.user_service.UserRepository")
@patch("app.domain.services.user_service.verify_password")
async def test_create_user_not_matching_password(
    mocked_verify_password, mocked_user_repository
):
    email = "test@test.com"
    password = "password"
    hashed_password = "hashed_password"
    user = entities.UserWithHashedPassword(
        id=uuid4(), email=email, hashed_password=hashed_password
    )
    mocked_user_repository_instance = (
        mocked_user_repository.return_value.__aenter__.return_value
    )
    mocked_user_repository_instance.get_user_by_email.return_value = user
    mocked_verify_password.return_value = False

    with pytest.raises(LoginFailed):
        assert await UserService.get_user_jwt(email=email, password=password)
    mocked_user_repository_instance.get_user_by_email.assert_awaited_once_with(email)
    mocked_verify_password.assert_called_once_with(password, hashed_password)


@patch("app.domain.services.user_service.UserRepository")
@patch("app.domain.services.user_service.verify_password")
@patch("app.domain.services.user_service.create_access_token")
async def test_create_user_matching_password(
    mocked_create_access_token, mocked_verify_password, mocked_user_repository
):
    email = "test@test.com"
    password = "password"
    hashed_password = "hashed_password"
    user = entities.UserWithHashedPassword(
        id=uuid4(), email=email, hashed_password=hashed_password
    )
    jwt = "jwt"
    mocked_user_repository_instance = (
        mocked_user_repository.return_value.__aenter__.return_value
    )
    mocked_user_repository_instance.get_user_by_email.return_value = user
    mocked_verify_password.return_value = True
    mocked_create_access_token.return_value = jwt

    assert await UserService.get_user_jwt(email=email, password=password) == jwt
    mocked_user_repository_instance.get_user_by_email.assert_awaited_once_with(email)
    mocked_verify_password.assert_called_once_with(password, hashed_password)
    mocked_create_access_token.assert_called_once_with(user.id)
