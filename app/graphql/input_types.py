from datetime import datetime
from typing import Optional

import strawberry

from app.graphql.validators import validate_email, validate_password


@strawberry.input
class TrainingInput:
    name: str
    start_time: datetime
    end_time: Optional[datetime]


@strawberry.input
class UserInput:
    email: str
    password: str

    def validate_email(self):
        validate_email(self.email)

    def validate_password(self):
        validate_password(self.password)

    def validate(self):
        self.validate_email()
        self.validate_password()
