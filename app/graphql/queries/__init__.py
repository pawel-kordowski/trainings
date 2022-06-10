import strawberry

from app.graphql.queries.friendship_requests import FriendshipRequestQuery
from app.graphql.queries.trainings import TrainingQuery


@strawberry.type
class Query(TrainingQuery, FriendshipRequestQuery):
    pass
