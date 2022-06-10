import enum


class ReactionTypeEnum(enum.Enum):
    like = "like"
    dislike = "dislike"


class TrainingVisibilityEnum(enum.Enum):
    public = "public"
    private = "private"
    only_friends = "only_friends"


class FriendshipRequestStatusEnum(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
