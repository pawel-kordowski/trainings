from uuid import UUID

import strawberry


@strawberry.type
class User:
    id: UUID
    email: str


@strawberry.type
class JWT:
    jwt: str
