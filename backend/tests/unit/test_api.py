"""
Тесты для API эндпоинтов
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

from app.main import app
from app.db.base_class import Base
from app.api.dependencies import get_db
from app.core.security import create_access_token
from app.models.user import User

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базу и таблицы для тестов
Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    Переопределяем зависимость для тестовой БД
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Переопределяем зависимость
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """
    Создаем тестовый клиент FastAPI
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def test_db():
    """
    Создаем тестовую БД
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def admin_token(test_db):
    """
    Создаем токен для административного пользователя
    """
    # Сначала проверяем, существует ли пользователь
    admin_user = test_db.query(User).filter(User.email == "admin@example.com").first()
    
    if not admin_user:
        # Создаем пользователя
        from app.core.security import get_password_hash
        admin_user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True
        )
        test_db.add(admin_user)
        test_db.commit()
        test_db.refresh(admin_user)
    
    # Создаем токен доступа
    access_token = create_access_token(
        subject=admin_user.email
    )
    return access_token

@pytest.fixture(scope="module")
def normal_user_token(test_db):
    """
    Создаем токен для обычного пользователя
    """
    # Сначала проверяем, существует ли пользователь
    normal_user = test_db.query(User).filter(User.email == "user@example.com").first()
    
    if not normal_user:
        # Создаем пользователя
        from app.core.security import get_password_hash
        normal_user = User(
            email="user@example.com",
            username="normaluser",
            hashed_password=get_password_hash("password"),
            is_active=True,
            is_superuser=False
        )
        test_db.add(normal_user)
        test_db.commit()
        test_db.refresh(normal_user)
    
    # Создаем токен доступа
    access_token = create_access_token(
        subject=normal_user.email
    )
    return access_token

# Тесты для API
def test_read_main(client):
    """
    Тест корневого эндпоинта
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Радио Камыши" in data["message"]

def test_login(client):
    """
    Тест входа в систему
    """
    login_data = {
        "username": "admin@example.com",
        "password": "admin"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_users_me(client, admin_token):
    """
    Тест получения информации о текущем пользователе
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_active"] is True
    assert data["is_superuser"] is True

def test_create_user(client, admin_token):
    """
    Тест создания пользователя (только для админа)
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123",
        "is_active": True,
        "is_superuser": False,
        "first_name": "New",
        "last_name": "User"
    }
    response = client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data

def test_get_users(client, admin_token):
    """
    Тест получения списка пользователей (только для админа)
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # admin, normal_user и newuser

def test_normal_user_cant_get_users(client, normal_user_token):
    """
    Тест, что обычный пользователь не может получить список пользователей
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403  # Forbidden

def test_create_track(client, normal_user_token):
    """
    Тест создания трека (для авторизованного пользователя)
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    track_data = {
        "title": "Test API Track",
        "artist": "Test Artist",
        "album": "Test Album",
        "genre": "Rock",
        "year": 2023,
        "file_path": "/path/to/api_test.mp3",
        "duration": 200.5,
        "file_size": 2048000,
        "format": "mp3",
        "bitrate": 320
    }
    response = client.post(
        "/api/v1/tracks/",
        headers=headers,
        json=track_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test API Track"
    assert data["artist"] == "Test Artist"
    assert "id" in data

def test_get_tracks(client, normal_user_token):
    """
    Тест получения списка треков
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    response = client.get("/api/v1/tracks/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Должен быть хотя бы один трек

def test_create_playlist(client, normal_user_token):
    """
    Тест создания плейлиста
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    playlist_data = {
        "name": "Test API Playlist",
        "description": "Playlist created via API test"
    }
    response = client.post(
        "/api/v1/playlists/",
        headers=headers,
        json=playlist_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test API Playlist"
    assert data["description"] == "Playlist created via API test"
    assert "id" in data
    
    # Сохраняем ID плейлиста для следующего теста
    playlist_id = data["id"]
    return playlist_id

def test_add_track_to_playlist(client, normal_user_token, test_db):
    """
    Тест добавления трека в плейлист
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    # Получаем ID существующего плейлиста
    from app.models.playlist import Playlist
    playlist = test_db.query(Playlist).first()
    assert playlist is not None, "Плейлист не найден для теста"
    
    # Получаем ID существующего трека
    from app.models.track import Track
    track = test_db.query(Track).first()
    assert track is not None, "Трек не найден для теста"
    
    # Данные для добавления трека в плейлист
    data = {
        "track_id": track.id,
        "position": 1
    }
    
    response = client.post(
        f"/api/v1/playlists/{playlist.id}/tracks",
        headers=headers,
        json=data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["playlist_id"] == playlist.id
    assert data["track_id"] == track.id
    assert data["position"] == 1

def test_get_playlist_tracks(client, normal_user_token, test_db):
    """
    Тест получения треков из плейлиста
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    # Получаем ID существующего плейлиста
    from app.models.playlist import Playlist
    playlist = test_db.query(Playlist).first()
    assert playlist is not None, "Плейлист не найден для теста"
    
    response = client.get(
        f"/api/v1/playlists/{playlist.id}/tracks",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Должен быть хотя бы один трек

def test_create_program(client, normal_user_token, test_db):
    """
    Тест создания программы
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    # Получаем ID существующего плейлиста
    from app.models.playlist import Playlist
    playlist = test_db.query(Playlist).first()
    assert playlist is not None, "Плейлист не найден для теста"
    
    program_data = {
        "name": "Test API Program",
        "description": "Program created via API test",
        "duration": 60,  # 60 минут
        "type": "music",
        "playlist_id": playlist.id
    }
    
    response = client.post(
        "/api/v1/programs/",
        headers=headers,
        json=program_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test API Program"
    assert data["duration"] == 60
    assert data["type"] == "music"
    assert "id" in data
    
    # Сохраняем ID программы для следующего теста
    program_id = data["id"]
    return program_id

def test_create_program_schedule(client, normal_user_token, test_db):
    """
    Тест создания расписания программы
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    # Получаем ID существующей программы
    from app.models.program import Program
    program = test_db.query(Program).first()
    assert program is not None, "Программа не найдена для теста"
    
    # Данные для создания расписания
    now = datetime.now().isoformat()
    end_time = datetime.now().replace(hour=datetime.now().hour + 1).isoformat()
    
    schedule_data = {
        "program_id": program.id,
        "start_time": now,
        "end_time": end_time,
        "repeat_type": "daily",
        "priority": 1
    }
    
    response = client.post(
        "/api/v1/programs/schedule",
        headers=headers,
        json=schedule_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["program_id"] == program.id
    assert data["repeat_type"] == "daily"
    assert data["priority"] == 1
    assert "id" in data

def test_get_program_schedule(client, normal_user_token):
    """
    Тест получения расписания программы
    """
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    response = client.get(
        "/api/v1/programs/schedule",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Должно быть хотя бы одно расписание

def test_get_broadcast_status(client):
    """
    Тест получения статуса вещания
    """
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    # Проверяем наличие ключевых полей в ответе
    assert isinstance(data, dict)
    # В тестовой среде не будет реального вещания, но должны быть базовые поля
    assert "host" in data
    assert "clients" in data
    assert "connections" in data 