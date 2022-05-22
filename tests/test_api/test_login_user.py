from unittest.mock import ANY

from app.jwt_tokens import get_user_id_from_token


def test_login_user_not_existing_user(client, db_session):
    query = """
    mutation {
        loginUser(
            input:{
                email: "email"
                password: "password"
            }
        ) {
            __typename
            ... on JWT{
                jwt
            }
            ... on Error{
                message
            }
        }
    }
    """
    response = client.post("/graphql", json={"query": query})

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["data"]["loginUser"] == {
        "__typename": "Error",
        "message": "Login failed",
    }


def test_login_user_existing_user_invalid_password(client, user):
    query = f"""
    mutation {{
        loginUser(
            input:{{
                email: "{user.email}"
                password: "invalid_password"
            }}
        ) {{
            __typename
            ... on JWT{{
                jwt
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
    assert response_json["data"]["loginUser"] == {
        "__typename": "Error",
        "message": "Login failed",
    }


def test_login_user_existing_user_successful(client, user):
    query = f"""
    mutation {{
        loginUser(
            input:{{
                email: "{user.email}"
                password: "password"
            }}
        ) {{
            __typename
            ... on JWT{{
                jwt
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
    payload = response_json["data"]["loginUser"]
    assert payload == {
        "__typename": "JWT",
        "jwt": ANY,
    }
    assert get_user_id_from_token(payload["jwt"]) == user.id
