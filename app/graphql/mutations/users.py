import strawberry

from app.domain.exceptions import EmailAlreadyExists
from app.domain.services.exceptions import LoginFailed
from app.domain.services.user_service import UserService
from app.graphql.exceptions import InvalidEmail, InvalidPassword
from app.graphql.input_types import UserInput
from app.graphql.types import JWT, Error, User


async def create_user(input: UserInput) -> User | Error:
    try:
        input.validate()
    except (InvalidEmail, InvalidPassword) as e:
        return Error(message=e.message)
    try:
        user = await UserService.create_user(email=input.email, password=input.password)
    except EmailAlreadyExists:
        return Error(message="Email address already taken")
    return User(id=user.id, email=user.email)


async def login_user(input: UserInput) -> JWT | Error:
    try:
        jwt = UserService.get_user_jwt(input.email, input.password)
    except LoginFailed as e:
        return Error(message=e.message)
    return JWT(jwt=jwt)


@strawberry.type
class UserMutation:
    create_user: User | Error = strawberry.mutation(resolver=create_user)
    login_user: JWT | Error = strawberry.mutation(resolver=login_user)
