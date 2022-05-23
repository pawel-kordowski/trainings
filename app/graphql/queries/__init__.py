import strawberry

from app.graphql.queries.trainings import TrainingQuery


@strawberry.type
class Query(TrainingQuery):
    pass
