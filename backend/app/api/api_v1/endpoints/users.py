from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_db, get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить текущего пользователя.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = Body(None),
    first_name: str = Body(None),
    last_name: str = Body(None),
    email: str = Body(None),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить собственные данные пользователя.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if first_name is not None:
        user_in.first_name = first_name
    if last_name is not None:
        user_in.last_name = last_name
    if email is not None:
        user_in.email = email
    
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Получить пользователя по ID.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="Недостаточно прав для этой операции"
        )
    return user


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_superuser),
) -> Any:
    """
    Получить список пользователей.
    Только для суперпользователей.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users 