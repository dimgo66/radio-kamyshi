from typing import Generator, Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import SessionLocal

# Токен получаем по пути /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Создаем типизированную аннотацию для повторного использования
DB = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DB, token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Зависимость для получения текущего аутентифицированного пользователя.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Невозможно подтвердить учетные данные",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Зависимость для получения текущего активного пользователя.
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


def get_current_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Зависимость для получения текущего пользователя-администратора.
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="Недостаточно прав доступа"
        )
    return current_user 