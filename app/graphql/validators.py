import re
import string

from app.config import PASSWORD_MIN_LENGTH
from app.graphql.exceptions import InvalidEmail, InvalidPassword


def validate_email(email: str):
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        raise InvalidEmail()


def validate_password(password: str):
    if len(password) < PASSWORD_MIN_LENGTH:
        raise InvalidPassword(
            message=f"Password too short, should have at least {PASSWORD_MIN_LENGTH} "
            "characters"
        )
    if password == password.upper():
        raise InvalidPassword(
            message="Password must contain at least one lowercase character"
        )
    if password == password.lower():
        raise InvalidPassword(
            message="Password must contain at least one uppercase character"
        )
    if not set(string.digits).intersection(password):
        raise InvalidPassword(message="Password must contain at least one digit")

    if not set(string.punctuation).intersection(password):
        raise InvalidPassword(
            message="Password must contain at least one special character"
        )
