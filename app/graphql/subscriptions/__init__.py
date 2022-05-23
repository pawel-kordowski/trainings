import strawberry

from app.graphql.subscriptions.trainings import TrainingSubscription


@strawberry.type
class Subscription(TrainingSubscription):
    pass
