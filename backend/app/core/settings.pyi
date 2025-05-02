from typing import Any, Dict, List, Optional, TypeVar, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl

class Settings:
    # Основные настройки
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool
    
    # Настройки API
    API_V1_STR: str
    
    # Для безопасности
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # База данных
    DATABASE_URL: str
    
    # Пользователи
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_PASSWORD: str

settings: Settings 