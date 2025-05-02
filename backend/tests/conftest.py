"""
Общие фикстуры и настройки для тестов
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Импортируем только необходимые модули для тестов моделей
# Комментируем полное приложение
# from app.main import app
from app.db.base_class import Base
# from app.core.config import settings
# from app.api.dependencies import get_db

# Создаем тестовую базу данных SQLite в памяти
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Создаем тестовый движок SQLAlchemy
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Создаем тестовую SessionLocal
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Создаем новую тестовую базу данных для каждого теста.
    """
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаляем таблицы после теста
        Base.metadata.drop_all(bind=engine)


# Закомментируем код, связанный с приложением FastAPI
# # Переопределяем зависимость get_db
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @pytest.fixture(scope="function")
# def client(db):
#     """
#     Создаем тестовый клиент для FastAPI с переопределенной зависимостью БД.
#     """
#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as client:
#         yield client
#     app.dependency_overrides = {} 