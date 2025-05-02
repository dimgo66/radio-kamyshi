from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.utils import verify_password_reset_token, generate_password_reset_token

router = APIRouter()


@router.post("/login/oauth", response_model=schemas.Token)
def login_oauth(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 совместимый токен логина, получаем токен для будущей аутентификации.
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=schemas.Token)
def login_json(
    *,
    db: Session = Depends(get_db),
    email: str = Body(...),
    password: str = Body(...)
) -> Any:
    """
    Логин через JSON для фронтенда.
    """
    user = crud.user.authenticate(
        db, email=email, password=password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user
    }


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Регистрация нового пользователя.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует",
        )
    
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким именем уже существует",
        )
    
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(get_db)) -> Any:
    """
    Восстановление пароля.
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким email не найден",
        )
    
    password_reset_token = generate_password_reset_token(email)
    
    # TODO: Отправить email с токеном сброса пароля
    # send_reset_password_email(email=email, token=password_reset_token)
    
    return {"msg": "Письмо со ссылкой для сброса пароля отправлено"}


@router.post("/reset-password", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    Сброс пароля.
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Недействительный токен")
    
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден",
        )
    
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    
    crud.user.update(db, db_obj=user, obj_in={"password": new_password})
    return {"msg": "Пароль успешно обновлен"} 