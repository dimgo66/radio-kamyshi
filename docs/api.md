# API документация "Радио Камыши"

## Общая информация

Все API запросы должны производиться на базовый URL: `/api/v1/`  
Аутентификация осуществляется через Bearer Token, который передается в заголовке `Authorization`.

Формат ответа:

```json
{
  "data": {}, // Данные запроса, может быть объектом или массивом
  "success": true, // Статус выполнения запроса
  "errors": [] // Массив ошибок, если они есть
}
```

## Аутентификация

### Вход в систему

```http
POST /api/v1/auth/login
```

Тело запроса:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Имя Пользователя"
  }
}
```

### Регистрация

```http
POST /api/v1/auth/register
```

Тело запроса:

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "Новый Пользователь"
}
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJ...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "newuser@example.com",
    "is_active": true,
    "is_superuser": false,
    "full_name": "Новый Пользователь"
  }
}
```

## Треки

### Получение списка треков

```http
GET /api/v1/tracks
```

Параметры запроса:

- `skip` (опционально): количество записей, которые нужно пропустить
- `limit` (опционально): максимальное количество записей
- `search` (опционально): поисковый запрос по названию, исполнителю и т.д.

Ответ:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Название трека",
      "artist": "Исполнитель",
      "album": "Альбом",
      "genre": "Жанр",
      "year": 2023,
      "duration": 180.5,
      "file_path": "/storage/tracks/track_1.mp3",
      "file_size": 3500000,
      "format": "mp3",
      "bitrate": 320,
      "waveform_data": "[0.1, 0.2, 0.3, ...]",
      "created_at": "2023-01-01T12:00:00",
      "updated_at": "2023-01-01T12:00:00"
    }
  ],
  "total": 100
}
```

### Получение конкретного трека

```
GET /api/v1/tracks/{track_id}
```

Ответ:
```json
{
  "id": 1,
  "title": "Название трека",
  "artist": "Исполнитель",
  "album": "Альбом",
  "genre": "Жанр",
  "year": 2023,
  "duration": 180.5,
  "file_path": "/storage/tracks/track_1.mp3",
  "file_size": 3500000,
  "format": "mp3",
  "bitrate": 320,
  "waveform_data": "[0.1, 0.2, 0.3, ...]",
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00"
}
```

### Загрузка трека

```
POST /api/v1/tracks
```

Тело запроса (multipart/form-data):
- `file`: аудиофайл
- `title`: название трека
- `artist` (опционально): исполнитель
- `album` (опционально): альбом
- `genre` (опционально): жанр
- `year` (опционально): год выпуска

Ответ:
```json
{
  "id": 1,
  "title": "Название трека",
  "artist": "Исполнитель",
  "album": "Альбом",
  "genre": "Жанр",
  "year": 2023,
  "duration": 180.5,
  "file_path": "/storage/tracks/track_1.mp3",
  "file_size": 3500000,
  "format": "mp3",
  "bitrate": 320,
  "waveform_data": "[0.1, 0.2, 0.3, ...]",
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00"
}
```

### Обновление трека

```
PUT /api/v1/tracks/{track_id}
```

Тело запроса:
```json
{
  "title": "Новое название",
  "artist": "Новый исполнитель",
  "album": "Новый альбом",
  "genre": "Новый жанр",
  "year": 2024
}
```

Ответ: обновленный объект трека.

### Удаление трека

```
DELETE /api/v1/tracks/{track_id}
```

Ответ:
```json
{
  "success": true,
  "message": "Трек успешно удален"
}
```

## Плейлисты

### Получение списка плейлистов

```
GET /api/v1/playlists
```

Параметры запроса:
- `skip` (опционально): количество записей, которые нужно пропустить
- `limit` (опционально): максимальное количество записей

Ответ:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Название плейлиста",
      "description": "Описание плейлиста",
      "track_count": 15,
      "duration": 3600,
      "created_at": "2023-01-01T12:00:00",
      "updated_at": "2023-01-01T12:00:00"
    }
  ],
  "total": 10
}
```

### Получение конкретного плейлиста с треками

```
GET /api/v1/playlists/{playlist_id}
```

Ответ:
```json
{
  "id": 1,
  "title": "Название плейлиста",
  "description": "Описание плейлиста",
  "tracks": [
    {
      "id": 1,
      "position": 1,
      "track": {
        "id": 5,
        "title": "Название трека",
        "artist": "Исполнитель",
        "duration": 180.5
      }
    }
  ],
  "track_count": 15,
  "duration": 3600,
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00"
}
```

### Создание плейлиста

```
POST /api/v1/playlists
```

Тело запроса:
```json
{
  "title": "Название плейлиста",
  "description": "Описание плейлиста",
  "track_ids": [1, 2, 3]
}
```

Ответ: созданный объект плейлиста.

### Добавление трека в плейлист

```
POST /api/v1/playlists/{playlist_id}/tracks
```

Тело запроса:
```json
{
  "track_id": 5,
  "position": 1
}
```

Ответ:
```json
{
  "id": 1,
  "playlist_id": 1,
  "track_id": 5,
  "position": 1
}
```

### Удаление трека из плейлиста

```
DELETE /api/v1/playlists/{playlist_id}/tracks/{track_id}
```

Ответ:
```json
{
  "success": true,
  "message": "Трек успешно удален из плейлиста"
}
```

## Программы эфира

### Получение списка программ

```
GET /api/v1/programs
```

Параметры запроса:
- `skip` (опционально): количество записей, которые нужно пропустить
- `limit` (опционально): максимальное количество записей
- `date` (опционально): дата в формате YYYY-MM-DD

Ответ:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Название программы",
      "description": "Описание программы",
      "start_time": "2023-01-01T12:00:00",
      "end_time": "2023-01-01T13:00:00",
      "playlist_id": 1,
      "playlist": {
        "id": 1,
        "title": "Название плейлиста",
        "track_count": 15
      },
      "status": "scheduled",
      "created_at": "2023-01-01T10:00:00",
      "updated_at": "2023-01-01T10:00:00"
    }
  ],
  "total": 5
}
```

### Получение текущей программы

```
GET /api/v1/programs/current
```

Ответ: объект текущей программы или null, если программы нет.

### Получение календаря программ

```
GET /api/v1/programs/calendar
```

Параметры запроса:
- `start_date`: начальная дата в формате YYYY-MM-DD
- `end_date`: конечная дата в формате YYYY-MM-DD

Ответ:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Название программы",
      "start_time": "2023-01-01T12:00:00",
      "end_time": "2023-01-01T13:00:00",
      "status": "scheduled"
    }
  ]
}
```

## Broadcast API

### Получение статуса вещания

```
GET /api/v1/broadcast/status
```

Ответ:
```json
{
  "server_status": "online",
  "sources": [
    {
      "mount": "/stream.mp3",
      "listeners": 10,
      "title": "Текущий трек",
      "artist": "Исполнитель",
      "genre": "Жанр",
      "bitrate": 128,
      "is_active": true
    }
  ],
  "clients": 12,
  "listeners": 10,
  "connections": 250
}
```

### Получение статуса конкретного потока

```
GET /api/v1/broadcast/stream/{mount}
```

Ответ:
```json
{
  "status": "online",
  "listeners": 10,
  "title": "Текущий трек",
  "artist": "Исполнитель",
  "bitrate": 128
}
```

### Обновление метаданных трека на потоке

```
POST /api/v1/broadcast/metadata/{mount}
```

Тело запроса:
```json
{
  "title": "Название трека",
  "artist": "Исполнитель"
}
```

Ответ:
```json
{
  "success": true,
  "message": "Метаданные успешно обновлены",
  "mount": "/stream.mp3",
  "title": "Название трека",
  "artist": "Исполнитель"
}
``` 