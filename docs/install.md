# Инструкция по установке "Радио Камыши"

## Системные требования

- Docker и Docker Compose
- 2GB RAM минимум
- 10GB свободного места на диске
- Доступ к порту 80 для веб-интерфейса и 8000 для Icecast

## Подготовка к установке

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/yourusername/radio-kamyshi.git
   cd radio-kamyshi
   ```

2. Создайте файл `.env` в корневой директории проекта:

   ```env
   # Базовые настройки
   SECRET_KEY=your_secret_key_here
   PROJECT_NAME=Radio Kamyshi
   SERVER_NAME=localhost
   SERVER_HOST=http://localhost

   # Настройки PostgreSQL
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=radio
   POSTGRES_SERVER=db

   # Настройки администратора
   FIRST_SUPERUSER=admin@example.com
   FIRST_SUPERUSER_PASSWORD=admin_password
   USERS_OPEN_REGISTRATION=false

   # Настройки Icecast
   ICECAST_URL=http://icecast:8000
   ICECAST_ADMIN_USER=admin
   ICECAST_ADMIN_PASSWORD=hackme
   ICECAST_SOURCE_PASSWORD=hackme
   ICECAST_RELAY_PASSWORD=hackme
   ICECAST_DEFAULT_MOUNT=/stream.mp3
   ```

3. Убедитесь, что у вас есть права на создание директорий в системе:

   ```bash
   mkdir -p volumes/postgres-data volumes/redis-data volumes/storage volumes/icecast-logs volumes/icecast-dump
   ```

## Установка и запуск

1. Соберите и запустите все сервисы в фоновом режиме:

   ```bash
   docker-compose up -d
   ```

2. Проверьте статус работы контейнеров:

   ```bash
   docker-compose ps
   ```

3. Запустите миграции базы данных:

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. Создайте начального пользователя (если не указан в .env):

   ```bash
   docker-compose exec backend python -m app.initial_data
   ```

## Проверка работоспособности

1. Веб-интерфейс должен быть доступен по адресу: `http://localhost`
2. API доступно по адресу: `http://localhost/api/v1`
3. Icecast доступен по адресу: `http://localhost:8000`

## Обновление системы

1. Остановите контейнеры:

   ```bash
   docker-compose down
   ```

2. Обновите код из репозитория:

   ```bash
   git pull
   ```

3. Пересоберите и запустите контейнеры:

   ```bash
   docker-compose up -d --build
   ```

4. При необходимости, запустите миграции:

   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Устранение неполадок

### Проблемы с доступом к базе данных

Проверьте статус контейнера базы данных:

```bash
docker-compose logs db
```

### Проблемы с веб-интерфейсом

Проверьте логи контейнера фронтенда:

```bash
docker-compose logs frontend
```

### Проблемы с Icecast

Проверьте логи Icecast:

```bash
docker-compose logs icecast
```

Также можно проверить файлы логов напрямую:

```bash
ls -la volumes/icecast-logs
```

## Резервное копирование

### База данных

Создать резервную копию:

```bash
docker-compose exec db pg_dump -U postgres radio > backup_$(date +%Y%m%d).sql
```

Восстановить из резервной копии:

```bash
cat backup_file.sql | docker-compose exec -T db psql -U postgres radio
```

### Файлы треков

Резервное копирование директории с медиафайлами:

```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz volumes/storage
``` 