from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.domain.exceptions import EmailAlreadyExists
from app.graphql.exceptions import InvalidPassword, InvalidEmail


@patch("app.graphql.input_types.validate_email")
@patch("app.graphql.input_types.validate_password")
@patch("app.graphql.mutations.users.UserService", autospec=True)
class TestCreateUser:
    email = "email"
    password = "password"

    def get_query(self):
        return f"""
        mutation {{
            createUser(
                input:{{
                    email: "{self.email}"
                    password: "{self.password}"
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

    def test_invalid_email(
        self,
        mocked_user_service,
        mocked_validate_password,
        mocked_validate_email,
        client,
    ):
        mocked_validate_email.side_effect = InvalidEmail()

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["createUser"] == {
            "__typename": "Error",
            "message": InvalidEmail.message,
        }
        mocked_validate_email.assert_called_once_with(self.email)

    def test_invalid_password(
        self,
        mocked_user_service,
        mocked_validate_password,
        mocked_validate_email,
        client,
    ):
        error_message = "Error message"
        mocked_validate_password.side_effect = InvalidPassword(message=error_message)

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["createUser"] == {
            "__typename": "Error",
            "message": error_message,
        }
        mocked_validate_password.assert_called_once_with(self.password)

    def test_new_email(
        self,
        mocked_user_service,
        mocked_validate_password,
        mocked_validate_email,
        client,
    ):
        user = entities.User(id=uuid4(), email=self.email)
        mocked_user_service.create_user.return_value = user

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["createUser"] == {
            "__typename": "User",
            "id": str(user.id),
            "email": user.email,
        }
        mocked_validate_password.assert_called_once_with(self.password)
        mocked_validate_email.assert_called_once_with(self.email)
        mocked_user_service.create_user.assert_awaited_once_with(
            email=self.email, password=self.password
        )

    def test_existing_email(
        self,
        mocked_user_service,
        mocked_validate_password,
        mocked_validate_email,
        client,
    ):
        mocked_user_service.create_user.side_effect = EmailAlreadyExists()

        response = client.post("/graphql", json={"query": self.get_query()})

        assert response.status_code == 200
        response_json = response.json()
        assert response_json["data"]["createUser"] == {
            "__typename": "Error",
            "message": "Email address already taken",
        }
        mocked_validate_password.assert_called_once_with(self.password)
        mocked_validate_email.assert_called_once_with(self.email)
        mocked_user_service.create_user.assert_awaited_once_with(
            email=self.email, password=self.password
        )
