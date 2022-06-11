class LoginFailed(Exception):
    message = "Login failed"


class AppError(Exception):
    message = None

    def __init__(self, message=None):
        if message:
            self.message = message


class ReceiverDoesNotExist(AppError):
    message = "Receiver does not exist"


class FriendshipRequestAlreadyCreated(AppError):
    message = "Friendship request already created"


class UsersAreAlreadyFriends(AppError):
    message = "Users are already friends"


class PendingFriendshipRequestForUserDoesNotExist(AppError):
    message = "Pending request for user does not exist"
