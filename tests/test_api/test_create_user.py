import pytest
from sqlalchemy import select

from app import models
from app.config import PASSWORD_MIN_LENGTH
from app.passwords import verify_password


@pytest.mark.parametrize(
    "email,password,expected_message",
    (
        ("a", "b", "Invalid email"),
        (
            "test@test.com",
            "b",
            f"Password too short, should have at least {PASSWORD_MIN_LENGTH} "
            "characters",
        ),
        (
            "test@test.com",
            "aaaaaaaa",
            "Password must contain at least one uppercase character",
        ),
        (
            "test@test.com",
            "AAAAAAAA",
            "Password must contain at least one lowercase character",
        ),
        ("test@test.com", "aAAAAAAA", "Password must contain at least one digit"),
        (
            "test@test.com",
            "aAAAAAA1",
            "Password must contain at least one special character",
        ),
    ),
)
def test_create_user_invalid_data(client, email, password, expected_message):
    query = f"""
    mutation {{
        createUser(
            input:{{
                email: "{email}"
                password: "{password}"
            }}
        ) {{
            __typename
            ... on User{{
                id
                email
            }}
            ... on Error{{
                message
            }}
        }}
    }}
    """
    response = client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createUser"] == {
        "__typename": "Error",
        "message": expected_message,
    }


def test_create_user_new_email(client, db_session):
    email = "test@test.com"
    password = "passwordA1!"
    query = f"""
    mutation {{
        createUser(
            input:{{
                email: "{email}"
                password: "{password}"
            }}
        ) {{
            __typename
            ... on User{{
                id
                email
            }}
            ... on Error{{
                message
            }}
        }}
    }}
    """
    response = client.post("/graphql", json={"query": query})

    sql = select(models.User)
    users_from_db = db_session.execute(sql).all()
    assert len(users_from_db) == 1
    user_from_db = users_from_db[0][0]
    assert user_from_db.email == email
    assert verify_password(password, user_from_db.hashed_password)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createUser"] == {
        "__typename": "User",
        "id": str(user_from_db.id),
        "email": email,
    }


def test_create_user_existing_email(client, db_session, user):
    password = "passwordA1!"
    query = f"""
    mutation {{
        createUser(
            input:{{
                email: "{user.email}"
                password: "{password}"
            }}
        ) {{
            __typename
            ... on User{{
                id
                email
            }}
            ... on Error{{
                message
            }}
        }}
    }}
    """
    response = client.post("/graphql", json={"query": query})

    sql = select(models.User)
    users_from_db = db_session.execute(sql).all()
    assert len(users_from_db) == 1
    assert users_from_db[0][0] == user

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createUser"] == {
        "__typename": "Error",
        "message": "Email address already taken",
    }
