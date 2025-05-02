# Radio Kamyshi Backend

Бэкенд для веб-приложения интернет-радиовещания Radio Kamyshi.

## Технологии

- **FastAPI** - современный высокопроизводительный фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - инструмент для миграций базы данных
- **PostgreSQL** - реляционная база данных
- **Pydantic** - библиотека для валидации данных
- **JWT** - для аутентификации и авторизации
- **Celery** - для асинхронной обработки задач
- **Redis** - для кэширования и хранения временных данных
- **Python-Multipart** - для загрузки файлов
- **Pytest** - для тестирования

## Структура проекта

```plaintext
backend/
├── alembic/            # Миграции базы данных
├── app/                # Основной код приложения
│   ├── api/            # Определения API
│   ├── core/           # Настройки и ядро приложения
│   ├── crud/           # Операции CRUD
│   ├── db/             # Настройки базы данных
│   ├── models/         # Модели SQLAlchemy
│   ├── schemas/        # Схемы Pydantic
│   ├── tasks/          # Задачи Celery
│   └── utils/          # Вспомогательные функции
├── storage/            # Хранилище для загружаемых файлов
├── migrations/         # Скрипты миграции (могут быть добавлены)
└── tests/              # Тесты
    ├── api/            # Тесты API
    ├── integration/    # Интеграционные тесты
    └── unit/           # Модульные тесты
```

## Запуск проекта

1. Установка зависимостей:

```bash
pip install -r requirements.txt
```

2. Настройка переменных окружения:

Скопируйте файл `.env.example` в `.env` и отредактируйте его:

```bash
cp .env.example .env
```

3. Запуск базы данных и Redis (через Docker):

```bash
docker-compose up -d postgres redis
```

4. Применение миграций:

```bash
alembic upgrade head
```

5. Запуск API:

```bash
uvicorn app.main:app --reload
```

6. Запуск воркеров Celery:

```bash
celery -A app.tasks.worker worker -l info
```

## Тестирование

В проекте реализованы следующие типы тестов:

1. **Модульные тесты (unit tests)** - проверяют работу отдельных компонентов системы изолированно
2. **Интеграционные тесты (integration tests)** - проверяют взаимодействие между компонентами
3. **API тесты** - проверяют работу API

### Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск только модульных тестов
pytest tests/unit/

# Запуск конкретного теста
pytest tests/unit/test_audio.py

# Запуск с выводом покрытия кода
pytest --cov=app

# Генерация HTML-отчета о покрытии
pytest --cov=app --cov-report=html
```

### Ключевые тестовые файлы

- `tests/unit/test_model_only.py` - тесты моделей данных
- `tests/unit/test_crud.py` - тесты CRUD операций
- `tests/unit/test_api_simplified.py` - упрощенные тесты API
- `tests/unit/test_security.py` - тесты безопасности
- `tests/unit/test_config.py` - тесты конфигурации
- `tests/unit/test_audio.py` - тесты обработки аудио
- `tests/unit/test_broadcast.py` - тесты вещания
- `tests/unit/test_playlist_with_tracks.py` - тесты плейлистов и треков
- `tests/unit/test_components_integration.py` - интеграционные тесты компонентов
- `tests/unit/test_filesystem.py` - тесты работы с файловой системой
- `tests/unit/test_cache.py` - тесты кэширования

## API документация

После запуска приложения документация Swagger доступна по адресу:

```plaintext
http://localhost:8000/docs
```

ReDoc версия:

```plaintext
http://localhost:8000/redoc
```

## Основные эндпоинты

- `/api/v1/auth/login` - вход в систему
- `/api/v1/users/` - управление пользователями
- `/api/v1/tracks/` - управление треками
- `/api/v1/playlists/` - управление плейлистами
- `/api/v1/programs/` - управление программами
- `/api/v1/programs/schedule` - управление расписанием
- `/api/v1/broadcast/` - управление вещанием

## Автор

Radio Kamyshi Team
