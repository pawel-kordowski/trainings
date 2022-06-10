import strawberry
from strawberry.types import Info

from app.domain.services.exceptions import (
    FriendshipRequestAlreadyCreated,
    ReceiverDoesNotExist,
    UsersAreAlreadyFriends,
)
from app.domain.services.friendship_request_service import FriendshipRequestService
from app.graphql.input_types import FriendshipRequestInput
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import Error
from app.graphql.types.friendship_requests import FriendshipRequest


async def send_friendship_request(
    info: Info, input: FriendshipRequestInput
) -> FriendshipRequest | Error:
    try:
        friendship_request = await FriendshipRequestService.create_friendship_request(
            sender_id=info.context["user_id"], receiver_id=input.user_id
        )
    except (
        ReceiverDoesNotExist,
        FriendshipRequestAlreadyCreated,
        UsersAreAlreadyFriends,
    ) as e:
        return Error(message=e.message)
    return FriendshipRequest.from_entity(friendship_request)


@strawberry.type
class FriendshipRequestMutation:
    send_friendship_request: FriendshipRequest | Error = strawberry.mutation(
        resolver=send_friendship_request, permission_classes=[IsAuthenticated]
    )
