import strawberry

from app.graphql.types.reactions import *  # noqa
from app.graphql.types.trainings import *  # noqa
from app.graphql.types.users import *  # noqa


@strawberry.type
class Error:
    message: str


@strawberry.type
class OK:
    message: str = "OK"
