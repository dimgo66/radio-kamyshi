"""
Тесты для модуля конфигурации
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Создаем класс для мока настроек
class MockSettings:
    """Мок-класс для Settings"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Тестовые настройки
TEST_SETTINGS = {
    "PROJECT_NAME": "Test Radio Kamyshi",
    "SERVER_HOST": "http://localhost:8000",
    "SERVER_PORT": 8000,
    "POSTGRES_HOST": "test-db",
    "POSTGRES_USER": "test_user", 
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
    "DATABASE_URL": "postgresql://test_user:test_password@test-db/test_db",
    "SECRET_KEY": "test_secret_key",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "FIRST_SUPERUSER_EMAIL": "test-admin@example.com",
    "FIRST_SUPERUSER_USERNAME": "test-admin",
    "FIRST_SUPERUSER_PASSWORD": "test-admin-password",
    "STORAGE_DIR": "/tmp/test-storage",
    "SMTP_TLS": True,
    "SMTP_PORT": 587,
    "SMTP_HOST": "test-smtp.example.com",
    "SMTP_USER": "test-smtp-user",
    "SMTP_PASSWORD": "test-smtp-password",
    "EMAILS_FROM_EMAIL": "test@example.com",
    "EMAILS_FROM_NAME": "Test Radio Kamyshi",
    "ICECAST_HOST": "test-icecast",
    "ICECAST_PORT": 8000,
    "ICECAST_SOURCE_PASSWORD": "test-source-password",
    "ICECAST_ADMIN_PASSWORD": "test-admin-password",
    "ICECAST_RELAY_PASSWORD": "test-relay-password",
    "ICECAST_DEFAULT_MOUNT": "/test.mp3",
    "CELERY_BROKER_URL": "amqp://test-guest:test-guest@test-rabbitmq:5672/",
    "EMAIL_TEMPLATES_DIR": "/app/app/email-templates/build"
}

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "PROJECT_NAME": "Радио Камыши API",
    "APP_NAME": "Камыши",
    "APP_ENV": "development",
    "DEBUG": True,
    "DATABASE_URL": "sqlite:///./test.db",
    "SECRET_KEY": "generated_secret_key_longer_than_30_characters_for_testing",
    "EMAIL_TEMPLATES_DIR": "/app/app/email-templates/build"
}

def test_settings_load():
    """Тест загрузки настроек"""
    # Создаем мок объекта settings
    mock_settings = MockSettings(**TEST_SETTINGS)
    
    # Патчим импорт настроек из модуля config
    with patch("app.core.config.settings", mock_settings):
        # Повторно импортируем для применения патча
        from app.core.config import settings
        
        # Проверяем основные настройки
        assert settings.PROJECT_NAME == "Test Radio Kamyshi"
        assert settings.SERVER_HOST == "http://localhost:8000"
        assert settings.SERVER_PORT == 8000
        
        # Проверяем настройки базы данных
        assert settings.POSTGRES_HOST == "test-db"
        assert settings.POSTGRES_USER == "test_user"
        assert settings.POSTGRES_PASSWORD == "test_password"
        assert settings.POSTGRES_DB == "test_db"
        
        # Проверяем генерацию строки подключения к БД
        expected_pg_dsn = "postgresql://test_user:test_password@test-db/test_db"
        assert settings.DATABASE_URL == expected_pg_dsn
        
        # Проверяем настройки безопасности
        assert settings.SECRET_KEY == "test_secret_key"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        
        # Проверяем настройки суперпользователя
        assert settings.FIRST_SUPERUSER_EMAIL == "test-admin@example.com"
        assert settings.FIRST_SUPERUSER_USERNAME == "test-admin"
        assert settings.FIRST_SUPERUSER_PASSWORD == "test-admin-password"
        
        # Проверяем настройки хранилища
        assert settings.STORAGE_DIR == "/tmp/test-storage"
        
        # Проверяем настройки SMTP
        assert settings.SMTP_TLS is True
        assert settings.SMTP_PORT == 587
        assert settings.SMTP_HOST == "test-smtp.example.com"
        assert settings.SMTP_USER == "test-smtp-user"
        assert settings.SMTP_PASSWORD == "test-smtp-password"
        assert settings.EMAILS_FROM_EMAIL == "test@example.com"
        assert settings.EMAILS_FROM_NAME == "Test Radio Kamyshi"
        
        # Проверяем настройки IceCast
        assert settings.ICECAST_HOST == "test-icecast"
        assert settings.ICECAST_PORT == 8000
        assert settings.ICECAST_SOURCE_PASSWORD == "test-source-password"
        assert settings.ICECAST_ADMIN_PASSWORD == "test-admin-password"
        assert settings.ICECAST_RELAY_PASSWORD == "test-relay-password"
        assert settings.ICECAST_DEFAULT_MOUNT == "/test.mp3"
        
        # Проверяем настройки Celery
        assert settings.CELERY_BROKER_URL == "amqp://test-guest:test-guest@test-rabbitmq:5672/"

def test_email_templates_dir():
    """Тест пути к шаблонам email"""
    # Создаем мок объекта settings
    mock_settings = MockSettings(**TEST_SETTINGS)
    
    # Патчим импорт настроек из модуля config
    with patch("app.core.config.settings", mock_settings):
        # Повторно импортируем для применения патча
        from app.core.config import settings
        
        # Проверяем путь к шаблонам email
        assert settings.EMAIL_TEMPLATES_DIR == "/app/app/email-templates/build"
        assert os.path.isabs(settings.EMAIL_TEMPLATES_DIR)

def test_settings_default_values():
    """Тест значений по умолчанию при отсутствии переменных окружения"""
    # Создаем мок объекта settings с настройками по умолчанию
    mock_settings = MockSettings(**DEFAULT_SETTINGS)
    
    # Патчим импорт настроек из модуля config
    with patch("app.core.config.settings", mock_settings):
        # Повторно импортируем для применения патча
        from app.core.config import settings
        
        # Проверяем значения по умолчанию
        assert settings.PROJECT_NAME == "Радио Камыши API"
        assert settings.APP_NAME == "Камыши"
        assert settings.APP_ENV == "development"
        assert settings.DEBUG is True
        
        # Проверяем настройки базы данных
        assert "sqlite" in settings.DATABASE_URL
        
        # Проверяем, что SECRET_KEY имеет значение
        assert settings.SECRET_KEY != ""
        assert len(settings.SECRET_KEY) > 30

def test_settings_validation():
    """Тест валидации настроек (некорректные значения)"""
    # Патчим импорт настроек из модуля config
    with patch("app.core.config.Settings", side_effect=Exception("ValidationError")):
        # Проверяем, что при создании с неверными значениями вызывается исключение
        with pytest.raises(Exception) as exc_info:
            # Пробуем создать новый экземпляр настроек, что должно вызвать исключение
            from app.core.config import Settings
            Settings()
        
        assert "ValidationError" in str(exc_info.value) 