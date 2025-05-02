"""
Интеграционные тесты для API и модуля вещания
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
from typing import List, Dict, Any, Optional
from jose import jwt

# Создаем базовый класс модели
Base = declarative_base()

# Модели данных
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    tracks = relationship("Track", back_populates="user")
    playlists = relationship("Playlist", back_populates="user")

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    file_path = Column(String, nullable=False)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="tracks")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track")

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist")

class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    track_id = Column(Integer, ForeignKey("tracks.id"))
    position = Column(Integer)
    
    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlist_tracks")

class Program(Base):
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # Длительность в минутах
    type = Column(String)  # music, talk, etc.
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=True)
    
    user = relationship("User")
    playlist = relationship("Playlist")
    schedules = relationship("ProgramSchedule", back_populates="program")

class ProgramSchedule(Base):
    __tablename__ = "program_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    repeat_type = Column(String)  # once, daily, weekly
    priority = Column(Integer, default=1)
    
    program = relationship("Program", back_populates="schedules")

# Класс для управления вещанием
class BroadcastManager:
    def __init__(self, db: Session):
        self.db = db
        self.current_track = None
        self.current_program = None
        self.broadcast_status = {
            "status": "offline",
            "current_track": None,
            "current_program": None,
            "listeners": 0,
            "started_at": None
        }
    
    def start_broadcast(self):
        if self.broadcast_status["status"] == "online":
            return False
        
        self.broadcast_status["status"] = "online"
        self.broadcast_status["started_at"] = datetime.now().isoformat()
        return True
    
    def stop_broadcast(self):
        if self.broadcast_status["status"] == "offline":
            return False
        
        self.broadcast_status["status"] = "offline"
        self.broadcast_status["current_track"] = None
        self.broadcast_status["current_program"] = None
        self.broadcast_status["started_at"] = None
        self.current_track = None
        self.current_program = None
        return True
    
    def set_current_track(self, track_id: int):
        track = self.db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return False
        
        self.current_track = track
        self.broadcast_status["current_track"] = {
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "album": track.album,
            "duration": track.duration
        }
        return True
    
    def set_current_program(self, program_id: int):
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return False
            
        self.current_program = program
        self.broadcast_status["current_program"] = {
            "id": program.id,
            "name": program.name,
            "description": program.description,
            "type": program.type,
            "duration": program.duration
        }
        
        # Если у программы есть плейлист, загружаем первый трек
        if program.playlist_id:
            playlist_track = self.db.query(PlaylistTrack).filter(
                PlaylistTrack.playlist_id == program.playlist_id
            ).order_by(PlaylistTrack.position).first()
            
            if playlist_track:
                self.set_current_track(playlist_track.track_id)
        
        return True
    
    def get_broadcast_status(self):
        return self.broadcast_status

# Создаем зависимость для получения менеджера вещания
class BroadcastManagerDependency:
    def __init__(self):
        self.instance = None
    
    def __call__(self, db: Session):
        if self.instance is None:
            self.instance = BroadcastManager(db)
        return self.instance

# Создаем функции безопасности
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(*, subject: str, expires_delta: Optional[timedelta] = None):
    """
    Создаёт JWT токен
    """
    to_encode = {"sub": subject}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базу и таблицы для тестов
Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии БД
def get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем тестовое приложение FastAPI
app = FastAPI()

# Создаем зависимость для авторизации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Зависимость для получения текущего пользователя
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось проверить учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Создаем broadcast manager
broadcast_manager_dependency = BroadcastManagerDependency()

# Эндпоинты API
@app.get("/api/v1/broadcast/status")
def get_broadcast_status(broadcast_manager: BroadcastManager = Depends(broadcast_manager_dependency)):
    """
    Получение статуса вещания
    """
    return broadcast_manager.get_broadcast_status()

@app.post("/api/v1/broadcast/start")
def start_broadcast(
    broadcast_manager: BroadcastManager = Depends(broadcast_manager_dependency),
    current_user: User = Depends(get_current_user)
):
    """
    Запуск вещания
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этой операции"
        )
    
    result = broadcast_manager.start_broadcast()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вещание уже запущено"
        )
    
    return {"status": "success", "message": "Вещание запущено"}

@app.post("/api/v1/broadcast/stop")
def stop_broadcast(
    broadcast_manager: BroadcastManager = Depends(broadcast_manager_dependency),
    current_user: User = Depends(get_current_user)
):
    """
    Остановка вещания
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этой операции"
        )
    
    result = broadcast_manager.stop_broadcast()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вещание уже остановлено"
        )
    
    return {"status": "success", "message": "Вещание остановлено"}

@app.post("/api/v1/broadcast/track/{track_id}")
def set_current_track(
    track_id: int,
    broadcast_manager: BroadcastManager = Depends(broadcast_manager_dependency),
    current_user: User = Depends(get_current_user)
):
    """
    Установка текущего трека
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этой операции"
        )
    
    result = broadcast_manager.set_current_track(track_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Трек с ID {track_id} не найден"
        )
    
    return {"status": "success", "message": f"Установлен трек {track_id}"}

@app.post("/api/v1/broadcast/program/{program_id}")
def set_current_program(
    program_id: int,
    broadcast_manager: BroadcastManager = Depends(broadcast_manager_dependency),
    current_user: User = Depends(get_current_user)
):
    """
    Установка текущей программы
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для этой операции"
        )
    
    result = broadcast_manager.set_current_program(program_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Программа с ID {program_id} не найдена"
        )
    
    return {"status": "success", "message": f"Установлена программа {program_id}"}

@app.post("/api/v1/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Вход в систему (для тестов)
    """
    user = db.query(User).filter(User.email == username).first()
    
    # В тестах просто проверяем, что пользователь существует
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен доступа
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

# Фикстуры для тестов
@pytest.fixture(scope="function")
def db():
    """Фикстура для тестовой БД"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    return TestClient(app)

@pytest.fixture
def admin_user(db):
    """Фикстура для создания административного пользователя"""
    user = db.query(User).filter(User.email == "admin@example.com").first()
    
    if not user:
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hashed_admin_password",
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

@pytest.fixture
def normal_user(db):
    """Фикстура для создания обычного пользователя"""
    user = db.query(User).filter(User.email == "user@example.com").first()
    
    if not user:
        user = User(
            email="user@example.com",
            username="user",
            hashed_password="hashed_user_password",
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

@pytest.fixture
def admin_token(admin_user):
    """Фикстура для получения токена администратора"""
    return create_access_token(subject=admin_user.email)

@pytest.fixture
def normal_token(normal_user):
    """Фикстура для получения токена обычного пользователя"""
    return create_access_token(subject=normal_user.email)

@pytest.fixture
def test_track(db, admin_user):
    """Фикстура для создания тестового трека"""
    track = Track(
        title="Test Track",
        artist="Test Artist",
        album="Test Album",
        genre="Rock",
        file_path="/tmp/test_track.mp3",
        duration=180.5,
        user_id=admin_user.id
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track

@pytest.fixture
def test_playlist(db, admin_user, test_track):
    """Фикстура для создания тестового плейлиста"""
    playlist = Playlist(
        name="Test Playlist",
        description="Playlist for testing",
        is_public=True,
        user_id=admin_user.id
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    # Добавляем трек в плейлист
    playlist_track = PlaylistTrack(
        playlist_id=playlist.id,
        track_id=test_track.id,
        position=1
    )
    db.add(playlist_track)
    db.commit()
    
    return playlist

@pytest.fixture
def test_program(db, admin_user, test_playlist):
    """Фикстура для создания тестовой программы"""
    program = Program(
        name="Test Program",
        description="Program for testing",
        duration=60,
        type="music",
        user_id=admin_user.id,
        playlist_id=test_playlist.id
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program

# Тесты
def test_get_broadcast_status(client):
    """Тест получения статуса вещания"""
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "offline"  # По умолчанию вещание выключено

def test_start_broadcast(client, admin_token):
    """Тест запуска вещания"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/api/v1/broadcast/start", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Проверяем, что статус изменился
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_set_current_track(client, admin_token, test_track):
    """Тест установки текущего трека"""
    # Сначала запускаем вещание
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/api/v1/broadcast/start", headers=headers)
    
    # Устанавливаем текущий трек
    response = client.post(f"/api/v1/broadcast/track/{test_track.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Проверяем, что трек установлен
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    assert data["current_track"] is not None
    assert data["current_track"]["id"] == test_track.id
    assert data["current_track"]["title"] == test_track.title

def test_set_current_program(client, admin_token, test_program):
    """Тест установки текущей программы"""
    # Сначала запускаем вещание
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/api/v1/broadcast/start", headers=headers)
    
    # Устанавливаем текущую программу
    response = client.post(f"/api/v1/broadcast/program/{test_program.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Проверяем, что программа установлена
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    assert data["current_program"] is not None
    assert data["current_program"]["id"] == test_program.id
    assert data["current_program"]["name"] == test_program.name
    
    # Также должен быть установлен трек из плейлиста программы
    assert data["current_track"] is not None

def test_stop_broadcast(client, admin_token):
    """Тест остановки вещания"""
    # Сначала запускаем вещание
    headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/api/v1/broadcast/start", headers=headers)
    
    # Останавливаем вещание
    response = client.post("/api/v1/broadcast/stop", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Проверяем, что статус изменился
    response = client.get("/api/v1/broadcast/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "offline"
    assert data["current_track"] is None
    assert data["current_program"] is None

def test_unauthorized_access(client, normal_token, test_track, test_program):
    """Тест доступа без прав администратора"""
    # Попытка запустить вещание без прав администратора
    headers = {"Authorization": f"Bearer {normal_token}"}
    
    response = client.post("/api/v1/broadcast/start", headers=headers)
    assert response.status_code == 403
    
    response = client.post(f"/api/v1/broadcast/track/{test_track.id}", headers=headers)
    assert response.status_code == 403
    
    response = client.post(f"/api/v1/broadcast/program/{test_program.id}", headers=headers)
    assert response.status_code == 403
    
    response = client.post("/api/v1/broadcast/stop", headers=headers)
    assert response.status_code == 403

def test_nonexistent_resources(client, admin_token):
    """Тест доступа к несуществующим ресурсам"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Запускаем вещание
    client.post("/api/v1/broadcast/start", headers=headers)
    
    # Попытка установить несуществующий трек
    response = client.post("/api/v1/broadcast/track/999", headers=headers)
    assert response.status_code == 404
    
    # Попытка установить несуществующую программу
    response = client.post("/api/v1/broadcast/program/999", headers=headers)
    assert response.status_code == 404 