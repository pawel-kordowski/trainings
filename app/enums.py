import enum

import strawberry


@strawberry.enum
class ReactionTypeEnum(enum.Enum):
    like = "like"
    dislike = "dislike"
