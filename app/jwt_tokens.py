from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt

from app import config


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_TIME_IN_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt
