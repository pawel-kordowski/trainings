from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.domain import entities
from app.domain.exceptions import EmailAlreadyExists
from app.graphql.exceptions import InvalidPassword, InvalidEmail


@patch("app.graphql.input_types.validate_email")
@patch("app.graphql.input_types.validate_password", MagicMock())
def test_create_user_invalid_email(mocked_validate_email, client):
    mocked_validate_email.side_effect = InvalidEmail()
    email = "email"
    password = "password"
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
        "message": InvalidEmail.message,
    }


@patch("app.graphql.input_types.validate_email", MagicMock())
@patch("app.graphql.input_types.validate_password")
def test_create_user_invalid_password(mocked_validate_password, client):
    error_message = "Error message"
    mocked_validate_password.side_effect = InvalidPassword(message=error_message)
    email = "email"
    password = "password"
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
        "message": error_message,
    }


@patch("app.graphql.input_types.validate_email", MagicMock())
@patch("app.graphql.input_types.validate_password", MagicMock())
@patch("app.graphql.mutations.users.UserService", autospec=True)
def test_create_user_new_email(mocked_user_service, client):
    email = "test@test.com"
    password = "passwordA1!"
    user_id = uuid4()
    mocked_user_service.create_user.return_value = entities.User(
        id=user_id, email=email
    )
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
        "__typename": "User",
        "id": str(user_id),
        "email": email,
    }
    mocked_user_service.create_user.assert_awaited_once_with(
        email=email, password=password
    )


@patch("app.graphql.input_types.validate_email", MagicMock())
@patch("app.graphql.input_types.validate_password", MagicMock())
@patch("app.graphql.mutations.users.UserService", autospec=True)
def test_create_user_existing_email(mocked_user_service, client):
    mocked_user_service.create_user.side_effect = EmailAlreadyExists()
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

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["createUser"] == {
        "__typename": "Error",
        "message": "Email address already taken",
    }
    mocked_user_service.create_user.assert_awaited_once_with(
        email=email, password=password
    )
