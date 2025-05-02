"""
Тесты для модуля трансляции (broadcast)
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
import enum
import json
from typing import List, Dict, Any, Optional

# Создаем базовый класс модели
Base = declarative_base()

# Перечисления
class ProgramType(enum.Enum):
    MUSIC = "music"
    PODCAST = "podcast"
    INTERVIEW = "interview"

class RepeatType(enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# Модели
class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String)
    file_path = Column(String, nullable=False)
    duration = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    track_id = Column(Integer, ForeignKey("tracks.id"))
    position = Column(Integer)
    
    track = relationship("Track")

class Program(Base):
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # в минутах
    type = Column(Enum(ProgramType))
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    playlist = relationship("Playlist")

class ProgramSchedule(Base):
    __tablename__ = "program_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    repeat_type = Column(Enum(RepeatType))
    priority = Column(Integer, default=1)
    
    program = relationship("Program")

class Broadcast(Base):
    __tablename__ = "broadcasts"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    current_track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)
    current_program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    started_at = Column(DateTime, nullable=True)
    
    current_track = relationship("Track")
    current_program = relationship("Program")

# Добавляем класс User
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

# Имитация модуля трансляции
class BroadcastService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_current_broadcast(self) -> Optional[Broadcast]:
        """Получить текущую трансляцию"""
        return self.db.query(Broadcast).filter(Broadcast.is_active.is_(True)).first()
    
    def start_broadcast(self, stream_url: str) -> Broadcast:
        """Запустить трансляцию"""
        # Проверить, есть ли уже активная трансляция
        active_broadcast = self.get_current_broadcast()
        if active_broadcast:
            # Обновляем существующую трансляцию
            active_broadcast.stream_url = stream_url
            active_broadcast.started_at = datetime.now()
            self.db.add(active_broadcast)
            self.db.commit()
            self.db.refresh(active_broadcast)
            return active_broadcast
        
        # Создаем новую трансляцию
        broadcast = Broadcast(
            stream_url=stream_url,
            is_active=True,
            started_at=datetime.now()
        )
        self.db.add(broadcast)
        self.db.commit()
        self.db.refresh(broadcast)
        return broadcast
    
    def stop_broadcast(self, broadcast_id: int) -> bool:
        """Остановить трансляцию"""
        broadcast = self.db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()
        if not broadcast:
            return False
        
        broadcast.is_active = False
        broadcast.current_track_id = None
        broadcast.current_program_id = None
        self.db.add(broadcast)
        self.db.commit()
        return True
    
    def set_current_track(self, broadcast_id: int, track_id: int) -> bool:
        """Установить текущий трек в трансляции"""
        broadcast = self.db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()
        if not broadcast:
            return False
        
        track = self.db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return False
        
        broadcast.current_track_id = track.id
        self.db.add(broadcast)
        self.db.commit()
        return True
    
    def set_current_program(self, broadcast_id: int, program_id: int) -> bool:
        """Установить текущую программу в трансляции"""
        broadcast = self.db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()
        if not broadcast:
            return False
        
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return False
        
        broadcast.current_program_id = program.id
        self.db.add(broadcast)
        self.db.commit()
        return True
    
    def get_broadcast_status(self, broadcast_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить статус трансляции"""
        if broadcast_id:
            broadcast = self.db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()
        else:
            broadcast = self.get_current_broadcast()
        
        if not broadcast:
            return {
                "status": "offline",
                "message": "Трансляция не найдена"
            }
        
        result = {
            "status": "online" if broadcast.is_active else "offline",
            "broadcast_id": broadcast.id,
            "stream_url": broadcast.stream_url,
            "started_at": broadcast.started_at.isoformat() if broadcast.started_at else None
        }
        
        if broadcast.current_track_id:
            track = broadcast.current_track
            result["current_track"] = {
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "duration": track.duration
            }
        
        if broadcast.current_program_id:
            program = broadcast.current_program
            result["current_program"] = {
                "id": program.id,
                "name": program.name,
                "type": program.type.value if program.type else None
            }
        
        return result

# Создаем тестовую базу данных
@pytest.fixture(scope="function")
def db():
    # Создаем тестовую базу данных SQLite в памяти
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    # Создаем тестовую сессию
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def broadcast_service(db):
    """Фикстура для сервиса трансляции"""
    return BroadcastService(db)

@pytest.fixture
def sample_user(db):
    """Фикстура для создания тестового пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def sample_tracks(db, sample_user):
    """Фикстура для создания тестовых треков"""
    tracks = []
    for i in range(1, 4):
        track = Track(
            title=f"Test Track {i}",
            artist=f"Test Artist {i}",
            file_path=f"/path/to/track{i}.mp3",
            duration=180 + i * 30,
            user_id=sample_user.id  # Добавляем user_id
        )
        db.add(track)
        tracks.append(track)
    
    db.commit()
    for track in tracks:
        db.refresh(track)
    
    return tracks

@pytest.fixture
def sample_playlist(db, sample_tracks, sample_user):
    """Фикстура для создания тестового плейлиста с треками"""
    playlist = Playlist(
        name="Test Playlist",
        description="Test playlist for broadcast",
        user_id=sample_user.id  # Добавляем user_id
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    # Добавляем треки в плейлист
    for i, track in enumerate(sample_tracks):
        playlist_track = PlaylistTrack(
            playlist_id=playlist.id,
            track_id=track.id,
            position=i+1
        )
        db.add(playlist_track)
    
    db.commit()
    return playlist

@pytest.fixture
def sample_program(db, sample_playlist, sample_user):
    """Фикстура для создания тестовой программы"""
    program = Program(
        name="Test Program",
        description="Test program for broadcast",
        duration=60,
        type=ProgramType.MUSIC,
        playlist_id=sample_playlist.id,
        user_id=sample_user.id  # Добавляем user_id
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program

# Тесты
def test_start_broadcast(broadcast_service):
    """Тест запуска трансляции"""
    stream_url = "http://example.com/stream"
    broadcast = broadcast_service.start_broadcast(stream_url)
    
    assert broadcast is not None
    assert broadcast.id is not None
    assert broadcast.stream_url == stream_url
    assert broadcast.is_active is True
    assert broadcast.started_at is not None

def test_stop_broadcast(broadcast_service):
    """Тест остановки трансляции"""
    # Сначала создаем трансляцию
    stream_url = "http://example.com/stream"
    broadcast = broadcast_service.start_broadcast(stream_url)
    
    # Останавливаем трансляцию
    result = broadcast_service.stop_broadcast(broadcast.id)
    assert result is True
    
    # Проверяем, что трансляция остановлена
    updated_broadcast = broadcast_service.db.query(Broadcast).filter(Broadcast.id == broadcast.id).first()
    assert updated_broadcast.is_active is False
    assert updated_broadcast.current_track_id is None
    assert updated_broadcast.current_program_id is None

def test_set_current_track(broadcast_service, sample_tracks):
    """Тест установки текущего трека"""
    # Создаем трансляцию
    broadcast = broadcast_service.start_broadcast("http://example.com/stream")
    
    # Устанавливаем текущий трек
    track = sample_tracks[0]
    result = broadcast_service.set_current_track(broadcast.id, track.id)
    assert result is True
    
    # Проверяем, что трек установлен
    updated_broadcast = broadcast_service.db.query(Broadcast).filter(Broadcast.id == broadcast.id).first()
    assert updated_broadcast.current_track_id == track.id

def test_set_current_program(broadcast_service, sample_program):
    """Тест установки текущей программы"""
    # Создаем трансляцию
    broadcast = broadcast_service.start_broadcast("http://example.com/stream")
    
    # Устанавливаем текущую программу
    result = broadcast_service.set_current_program(broadcast.id, sample_program.id)
    assert result is True
    
    # Проверяем, что программа установлена
    updated_broadcast = broadcast_service.db.query(Broadcast).filter(Broadcast.id == broadcast.id).first()
    assert updated_broadcast.current_program_id == sample_program.id

def test_get_broadcast_status(broadcast_service, sample_tracks, sample_program):
    """Тест получения статуса трансляции"""
    # Создаем трансляцию
    broadcast = broadcast_service.start_broadcast("http://example.com/stream")
    
    # Устанавливаем текущий трек и программу
    track = sample_tracks[0]
    broadcast_service.set_current_track(broadcast.id, track.id)
    broadcast_service.set_current_program(broadcast.id, sample_program.id)
    
    # Получаем статус трансляции
    status = broadcast_service.get_broadcast_status(broadcast.id)
    
    # Проверяем статус
    assert status["status"] == "online"
    assert status["broadcast_id"] == broadcast.id
    assert status["stream_url"] == "http://example.com/stream"
    assert "started_at" in status
    
    # Проверяем информацию о треке
    assert "current_track" in status
    assert status["current_track"]["id"] == track.id
    assert status["current_track"]["title"] == track.title
    assert status["current_track"]["artist"] == track.artist
    
    # Проверяем информацию о программе
    assert "current_program" in status
    assert status["current_program"]["id"] == sample_program.id
    assert status["current_program"]["name"] == sample_program.name
    assert status["current_program"]["type"] == "music"

def test_offline_broadcast_status(broadcast_service):
    """Тест статуса при отсутствии трансляции"""
    # Получаем статус без существующей трансляции
    status = broadcast_service.get_broadcast_status()
    
    assert status["status"] == "offline"
    assert "message" in status 