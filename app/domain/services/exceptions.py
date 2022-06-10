class LoginFailed(Exception):
    message = "Login failed"


class ReceiverDoesNotExist(Exception):
    message = "Receiver does not exist"


class FriendshipRequestAlreadyCreated(Exception):
    message = "Friendship request already created"
