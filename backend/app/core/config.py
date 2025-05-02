import os
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "Камыши"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Настройки API
    API_V1_STR: str = "/api/v1"
    
    # Пути к директориям
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MEDIA_DIR: str = os.environ.get("MEDIA_ROOT", os.path.join(BASE_DIR, "..", "media"))
    PLAYLISTS_DIR: str = os.environ.get("PLAYLISTS_ROOT", os.path.join(BASE_DIR, "..", "playlists"))
    
    # База данных
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "kamyshi_user")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "password123")
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "kamyshi")
    
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Redis и Celery
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT: str = os.environ.get("REDIS_PORT", "6379")
    REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "redis123")
    
    REDIS_URL: str = os.environ.get(
        "REDIS_URL",
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
    )
    
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # Безопасность
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your_jwt_secret_key")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    # CORS
    CORS_ORIGINS: List[str] = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Icecast
    ICECAST_HOST: str = os.environ.get("ICECAST_HOSTNAME", "localhost")
    ICECAST_PORT: str = os.environ.get("ICECAST_PORT", "8010")
    ICECAST_SOURCE_PASSWORD: str = os.environ.get("ICECAST_SOURCE_PASSWORD", "hackme")
    ICECAST_ADMIN_USER: str = os.environ.get("ICECAST_ADMIN_USER", "admin")
    ICECAST_ADMIN_PASSWORD: str = os.environ.get("ICECAST_ADMIN_PASSWORD", "hackme")
    
    # Subapse
    SUBAPSE_HOST: str = "subapse"
    SUBAPSE_PORT: int = 8080
    SUBAPSE_API_KEY: Optional[str] = None
    
    # Storage
    STORAGE_DIR: str = "/app/storage"
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Радио Камыши"
    SENTRY_DSN: Optional[HttpUrl] = None

    @field_validator("SENTRY_DSN", mode="before")
    def sentry_dsn_can_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is None or len(v) == 0:
            return None
        return v

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], info: Any) -> str:
        if not v:
            return info.data.get("PROJECT_NAME", "")
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    def get_emails_enabled(cls, v: bool, info: Any) -> bool:
        return bool(
            info.data.get("SMTP_HOST")
            and info.data.get("SMTP_PORT")
            and info.data.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = False
    
    # Icecast settings
    ICECAST_URL: str = "http://localhost:8000"
    ICECAST_RELAY_PASSWORD: Optional[str] = "hackme"
    ICECAST_DEFAULT_MOUNT: str = "/stream.mp3"

    # Разрешаем дополнительные поля в настройках
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings() 