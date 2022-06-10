import strawberry

from app.graphql.mutations.friendship_requests import FriendshipRequestMutation
from app.graphql.mutations.trainings import TrainingMutation
from app.graphql.mutations.users import UserMutation


@strawberry.type
class Mutation(UserMutation, TrainingMutation, FriendshipRequestMutation):
    pass
