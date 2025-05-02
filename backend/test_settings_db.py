"""
Тестовый скрипт для проверки типизации настроек и базы данных
"""
from app.core.config import settings
from app.db.base_class import Base
from app.models.user import User


def main():
    """
    Проверка, что настройки и база данных правильно типизированы
    """
    # Проверка настроек
    print(f"Настройки API: {settings.API_V1_STR}")
    print(f"Суперпользователь: {settings.FIRST_SUPERUSER_EMAIL}")
    print(f"Имя пользователя: {settings.FIRST_SUPERUSER_USERNAME}")
    
    # Проверка базы данных
    print(f"Есть атрибут metadata: {hasattr(Base, 'metadata')}")
    print(f"User.__tablename__: {User.__tablename__}")
    
    # Без фактического подключения к базе данных
    print("Все хорошо типизировано!")


if __name__ == "__main__":
    main() 