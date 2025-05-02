"""
Скрипт для инициализации базы данных.
"""
import logging
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine


logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    Инициализировать базу данных с необходимыми таблицами и начальными данными.
    """
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы успешно созданы")
    
    # Добавляем начального суперпользователя, если он еще не существует
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            first_name="Admin",
            last_name="Admin",
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        logger.info(f"Суперпользователь {user.email} создан") 