import strawberry
from strawberry.types import Info

from app.domain.services.friendship_request_service import FriendshipRequestService
from app.graphql.permissions import IsAuthenticated
from app.graphql.types.friendship_requests import FriendshipRequest


async def get_my_sent_friendship_requests(info: Info) -> list[FriendshipRequest]:
    friendship_requests = (
        await FriendshipRequestService.get_pending_requests_sent_by_user(
            user_id=info.context["user_id"]
        )
    )

    return [
        FriendshipRequest.from_entity(friendship_request)
        for friendship_request in friendship_requests
    ]


async def get_my_received_friendship_requests(info: Info) -> list[FriendshipRequest]:
    friendship_requests = (
        await FriendshipRequestService.get_pending_requests_received_by_user(
            user_id=info.context["user_id"]
        )
    )

    return [
        FriendshipRequest.from_entity(friendship_request)
        for friendship_request in friendship_requests
    ]


@strawberry.type
class FriendshipRequestQuery:
    my_sent_friendship_requests: list[FriendshipRequest] = strawberry.field(
        resolver=get_my_sent_friendship_requests, permission_classes=[IsAuthenticated]
    )
    my_received_friendship_requests: list[FriendshipRequest] = strawberry.field(
        resolver=get_my_received_friendship_requests,
        permission_classes=[IsAuthenticated],
    )
