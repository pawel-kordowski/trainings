class InvalidEmail(Exception):
    message = "Invalid email"


class InvalidPassword(Exception):
    def __init__(self, message):
        self.message = message
