from datetime import datetime, timedelta
from typing import Optional

import jwt

from app.core.config import settings


def generate_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "nbf": datetime.utcnow(),
        "sub": email,
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None 