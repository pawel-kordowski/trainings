import strawberry

from app.graphql.mutations import Mutation
from app.graphql.queries import Query
from app.graphql.subscriptions import Subscription

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
