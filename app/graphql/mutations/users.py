import strawberry

from app.database import get_session
from app.domain.exceptions import EmailAlreadyExists
from app.domain.repositories import PostgresRepository
from app.graphql.exceptions import InvalidEmail, InvalidPassword
from app.graphql.input_types import UserInput
from app.graphql.types import JWT, Error, User
from app.jwt_tokens import create_access_token
from app.passwords import get_password_hash, verify_password


async def create_user(input: UserInput) -> User | Error:
    try:
        input.validate()
    except (InvalidEmail, InvalidPassword) as e:
        return Error(message=e.message)
    hashed_password = get_password_hash(input.password)
    async with get_session() as s:
        repository = PostgresRepository(s)
        try:
            user = await repository.create_user(
                email=input.email, hashed_password=hashed_password
            )
        except EmailAlreadyExists:
            return Error(message="Email address already taken")
    return User(id=user.id, email=user.email)


async def login_user(input: UserInput) -> JWT | Error:
    async with get_session() as s:
        repository = PostgresRepository(s)
        user = await repository.get_user_by_email(input.email)
    if not user or not verify_password(input.password, user.hashed_password):
        return Error(message="Login failed")
    return JWT(jwt=create_access_token(user.id))


@strawberry.type
class UserMutation:
    create_user: User | Error = strawberry.mutation(resolver=create_user)
    login_user: JWT | Error = strawberry.mutation(resolver=login_user)
