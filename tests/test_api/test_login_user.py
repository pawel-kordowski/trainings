from unittest.mock import patch

from app.domain.services.exceptions import LoginFailed


@patch("app.graphql.mutations.users.UserService")
class TestLoginUser:
    email = "email"
    password = "password"

    def get_query(self):
        return f"""
        mutation {{
            loginUser(
                input:{{
                    email: "{self.email}"
                    password: "{self.password}"
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

    def test_failed(self, mocked_user_service, client):
        mocked_user_service.get_user_jwt.side_effect = LoginFailed()

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["loginUser"] == {
            "__typename": "Error",
            "message": "Login failed",
        }

    def test_successful(self, mocked_user_service, client):
        jwt = "jwt"
        mocked_user_service.get_user_jwt.return_value = jwt

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["loginUser"] == {
            "__typename": "JWT",
            "jwt": jwt,
        }
