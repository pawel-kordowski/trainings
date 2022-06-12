import strawberry
from strawberry.types import Info

from app.domain.services.exceptions import AppError
from app.domain.services.friendship_request_service import FriendshipRequestService
from app.graphql.input_types import FriendshipRequestIDInput, FriendshipRequestInput
from app.graphql.permissions import IsAuthenticated
from app.graphql.types import OK, Error
from app.graphql.types.friendship_requests import FriendshipRequest


async def send_friendship_request(
    info: Info, input: FriendshipRequestInput
) -> FriendshipRequest | Error:
    try:
        friendship_request = await FriendshipRequestService.create_friendship_request(
            sender_id=info.context["user_id"], receiver_id=input.user_id
        )
    except AppError as e:
        return Error(message=e.message)
    return FriendshipRequest.from_entity(friendship_request)


async def accept_friendship_request(
    info: Info, input: FriendshipRequestIDInput
) -> OK | Error:
    try:
        await FriendshipRequestService.accept_friendship_request(
            user_id=info.context["user_id"],
            friendship_request_id=input.friendship_request_id,
        )
    except AppError as e:
        return Error(message=e.message)
    return OK()


async def reject_friendship_request(
    info: Info, input: FriendshipRequestIDInput
) -> OK | Error:
    try:
        await FriendshipRequestService.reject_friendship_request(
            user_id=info.context["user_id"],
            friendship_request_id=input.friendship_request_id,
        )
    except AppError as e:
        return Error(message=e.message)
    return OK()


async def cancel_friendship_request(
    info: Info, input: FriendshipRequestIDInput
) -> OK | Error:
    try:
        await FriendshipRequestService.cancel_friendship_request(
            user_id=info.context["user_id"],
            friendship_request_id=input.friendship_request_id,
        )
    except AppError as e:
        return Error(message=e.message)
    return OK()


@strawberry.type
class FriendshipRequestMutation:
    send_friendship_request: FriendshipRequest | Error = strawberry.mutation(
        resolver=send_friendship_request, permission_classes=[IsAuthenticated]
    )
    accept_friendship_request: OK | Error = strawberry.mutation(
        resolver=accept_friendship_request, permission_classes=[IsAuthenticated]
    )
    reject_friendship_request: OK | Error = strawberry.mutation(
        resolver=reject_friendship_request, permission_classes=[IsAuthenticated]
    )
    cancel_friendship_request: OK | Error = strawberry.mutation(
        resolver=cancel_friendship_request, permission_classes=[IsAuthenticated]
    )
