from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app import config


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_TIME_IN_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def get_user_id_from_token(token: str) -> UUID | None:
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
    except JWTError:
        return None
    user_id = payload.get("sub")
    if user_id is not None:
        return UUID(user_id)
