import typing
from uuid import UUID

from jose import JWTError, jwt
from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry import BasePermission
from strawberry.types import Info

from app import config


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request: typing.Union[Request, WebSocket] = info.context["request"]

        if "Authorization" in request.headers or "auth" in request.query_params:
            header: str = request.headers.get(
                "Authorization"
            ) or request.query_params.get("auth")
            bearer, _, token = header.partition(" ")
            if bearer.lower() != "bearer":
                return False
            try:
                payload = jwt.decode(
                    token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
                )
            except JWTError:
                return False
            user_id: str = payload.get("sub")
            if user_id is None:
                return False
            info.context["user_id"] = UUID(user_id)
            return True

        return False
