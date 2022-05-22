import pytest

from app.config import PASSWORD_MIN_LENGTH
from app.graphql.exceptions import InvalidEmail, InvalidPassword
from app.graphql.validators import validate_email, validate_password


def test_validate_email_correct():
    validate_email("test@test.com")


@pytest.mark.parametrize(
    "email", ("", "a", "a@", "a@b", "@test.com", "test.com@a", "test@@test.com")
)
def test_validate_email_incorrect(email):
    with pytest.raises(InvalidEmail):
        validate_email(email)


def test_validate_password_correct():
    validate_password("passwordA1!")


@pytest.mark.parametrize(
    "password,expected_message",
    (
        (
            "",
            f"Password too short, should have at least {PASSWORD_MIN_LENGTH} "
            "characters",
        ),
        ("aaaaaaaa", "Password must contain at least one uppercase character"),
        ("AAAAAAAA", "Password must contain at least one lowercase character"),
        ("aAAAAAAA", "Password must contain at least one digit"),
        ("aAAAAAA1", "Password must contain at least one special character"),
    ),
)
def test_validate_password_incorrect(password, expected_message):
    with pytest.raises(InvalidPassword) as e:
        validate_password(password)
    assert e.value.message == expected_message
