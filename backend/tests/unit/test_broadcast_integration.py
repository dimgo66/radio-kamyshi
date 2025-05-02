"""
Интеграционные тесты для модулей вещания и плейлистов
"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, and_, text, select
from sqlalchemy.sql import operators
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
from typing import List, Dict, Any, Optional, Union, cast, ClassVar

# Создаем базовый класс модели
Base = declarative_base()

# Модели данных для тестов
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    tracks = relationship("Track", back_populates="user")
    playlists = relationship("Playlist", back_populates="user")

class Track(Base):
    __tablename__ = "track"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    file_path = Column(String, nullable=False)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))
    
    user = relationship("User", back_populates="tracks")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track")

class Playlist(Base):
    __tablename__ = "playlist"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))
    
    user = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist")

class PlaylistTrack(Base):
    __tablename__ = "playlist_track"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlist.id"))
    track_id = Column(Integer, ForeignKey("track.id"))
    position = Column(Integer)
    
    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlist_tracks")

class Program(Base):
    __tablename__ = "program"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # Длительность в минутах
    type = Column(String)  # music, talk, etc.
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))
    playlist_id = Column(Integer, ForeignKey("playlist.id"), nullable=True)
    
    user = relationship("User")
    playlist = relationship("Playlist")
    schedules = relationship("ProgramSchedule", back_populates="program")

class ProgramSchedule(Base):
    __tablename__ = "program_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("program.id"))
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
        # Используем правильный запрос
        stmt = select(Track).where(Track.id == track_id)
        track = self.db.execute(stmt).scalars().first()
        
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
        # Используем правильный запрос
        stmt = select(Program).where(Program.id == program_id)
        program = self.db.execute(stmt).scalars().first()
        
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
            # Используем правильный запрос
            stmt = select(PlaylistTrack).where(
                PlaylistTrack.playlist_id == program.playlist_id
            ).order_by(PlaylistTrack.position.asc())
            playlist_track = self.db.execute(stmt).scalars().first()
            
            if playlist_track:
                self.set_current_track(playlist_track.track_id)
        
        return True
    
    def get_broadcast_status(self):
        return self.broadcast_status
    
    def get_next_track_from_playlist(self, playlist_id: int, current_position: Optional[int] = None):
        """Получает следующий трек из плейлиста"""
        if current_position is None:
            # Если позиция не указана, берем первый трек
            stmt = select(PlaylistTrack).where(
                PlaylistTrack.playlist_id == playlist_id
            ).order_by(PlaylistTrack.position.asc())
            next_track = self.db.execute(stmt).scalars().first()
        else:
            # Если позиция указана, берем следующий трек
            # Используем текстовый SQL запрос для избежания проблем с типами
            stmt = text(
                "SELECT * FROM playlist_track "
                "WHERE playlist_id = :playlist_id AND position > :position "
                "ORDER BY position ASC LIMIT 1"
            )
            result = self.db.execute(
                stmt, 
                {"playlist_id": playlist_id, "position": current_position}
            )
            next_track = result.fetchone()
            
            # Если следующего трека нет, возвращаемся к первому
            if not next_track:
                stmt = select(PlaylistTrack).where(
                    PlaylistTrack.playlist_id == playlist_id
                ).order_by(PlaylistTrack.position.asc())
                next_track = self.db.execute(stmt).scalars().first()
            else:
                # Получаем объект трека из результата SQL запроса
                track_id = next_track.track_id
                stmt = select(Track).where(Track.id == track_id)
                track = self.db.execute(stmt).scalar_one_or_none()
                return track
        
        return next_track.track if next_track else None

# Фикстуры для тестов
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
def broadcast_manager(db):
    """Фикстура для менеджера вещания"""
    return BroadcastManager(db)

@pytest.fixture
def test_user(db):
    """Фикстура для создания тестового пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_tracks(db, test_user):
    """Фикстура для создания тестовых треков"""
    tracks = []
    
    # Создаем несколько треков разных жанров
    track_data = [
        {
            "title": "Rock Song", 
            "artist": "Rock Artist", 
            "album": "Rock Album", 
            "genre": "Rock", 
            "file_path": "/tmp/rock_song.mp3", 
            "duration": 180.5
        },
        {
            "title": "Pop Song", 
            "artist": "Pop Artist", 
            "album": "Pop Album", 
            "genre": "Pop", 
            "file_path": "/tmp/pop_song.mp3", 
            "duration": 210.75
        },
        {
            "title": "Jazz Improvisation", 
            "artist": "Jazz Musician", 
            "album": "Jazz Collection", 
            "genre": "Jazz", 
            "file_path": "/tmp/jazz_track.mp3", 
            "duration": 360.25
        }
    ]
    
    for data in track_data:
        track = Track(user_id=test_user.id, **data)
        db.add(track)
        tracks.append(track)
    
    db.commit()
    
    # Обновляем объекты треков из БД
    for track in tracks:
        db.refresh(track)
    
    return tracks

@pytest.fixture
def test_playlist(db, test_user, test_tracks):
    """Фикстура для создания тестового плейлиста с треками"""
    playlist = Playlist(
        name="Test Playlist",
        description="Playlist for testing",
        is_public=True,
        user_id=test_user.id
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_track = PlaylistTrack(
            playlist_id=playlist.id,
            track_id=track.id,
            position=i+1
        )
        db.add(playlist_track)
    
    db.commit()
    return playlist

@pytest.fixture
def test_program(db, test_user, test_playlist):
    """Фикстура для создания тестовой программы с плейлистом"""
    program = Program(
        name="Test Music Program",
        description="Program for testing",
        duration=60,  # 60 минут
        type="music",
        user_id=test_user.id,
        playlist_id=test_playlist.id
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    
    # Создаем расписание для программы
    now = datetime.now()
    schedule = ProgramSchedule(
        program_id=program.id,
        start_time=now,
        end_time=now + timedelta(hours=1),
        repeat_type="daily",
        priority=1
    )
    db.add(schedule)
    db.commit()
    
    return program

# Тесты
def test_broadcast_with_playlist(broadcast_manager, test_playlist, test_tracks):
    """Тест вещания плейлиста"""
    # Запускаем вещание
    assert broadcast_manager.start_broadcast() is True
    
    # Статус должен быть "online"
    status = broadcast_manager.get_broadcast_status()
    assert status["status"] == "online"
    
    # Устанавливаем текущий трек
    track = test_tracks[0]
    assert broadcast_manager.set_current_track(track.id) is True
    
    # Проверяем, что трек установлен
    status = broadcast_manager.get_broadcast_status()
    assert status["current_track"] is not None
    assert status["current_track"]["title"] == track.title
    
    # Получаем следующий трек из плейлиста
    next_track = broadcast_manager.get_next_track_from_playlist(test_playlist.id, 1)
    assert next_track is not None
    assert next_track.title == test_tracks[1].title
    
    # Устанавливаем следующий трек
    assert broadcast_manager.set_current_track(next_track.id) is True
    
    # Проверяем, что трек изменился
    status = broadcast_manager.get_broadcast_status()
    assert status["current_track"]["title"] == next_track.title

def test_broadcast_with_program(broadcast_manager, test_program):
    """Тест вещания программы"""
    # Запускаем вещание
    assert broadcast_manager.start_broadcast() is True
    
    # Устанавливаем текущую программу
    assert broadcast_manager.set_current_program(test_program.id) is True
    
    # Проверяем, что программа установлена
    status = broadcast_manager.get_broadcast_status()
    assert status["current_program"] is not None
    assert status["current_program"]["name"] == test_program.name
    
    # Также должен быть автоматически установлен первый трек из плейлиста программы
    assert status["current_track"] is not None
    
    # Останавливаем вещание
    assert broadcast_manager.stop_broadcast() is True
    
    # Проверяем, что статус изменился и данные сброшены
    status = broadcast_manager.get_broadcast_status()
    assert status["status"] == "offline"
    assert status["current_track"] is None
    assert status["current_program"] is None

def test_next_track_cycling(broadcast_manager, test_playlist, test_tracks):
    """Тест цикличного воспроизведения треков из плейлиста"""
    # Запускаем вещание
    assert broadcast_manager.start_broadcast() is True
    
    # Получаем первый трек
    first_track = broadcast_manager.get_next_track_from_playlist(test_playlist.id)
    assert first_track is not None
    assert first_track.title == test_tracks[0].title
    
    # Получаем второй трек (после первого)
    second_track = broadcast_manager.get_next_track_from_playlist(test_playlist.id, 1)
    assert second_track is not None
    assert second_track.title == test_tracks[1].title
    
    # Получаем третий трек (после второго)
    third_track = broadcast_manager.get_next_track_from_playlist(test_playlist.id, 2)
    assert third_track is not None
    assert third_track.title == test_tracks[2].title
    
    # Получаем следующий трек после последнего (должен быть первый)
    next_track = broadcast_manager.get_next_track_from_playlist(test_playlist.id, 3)
    assert next_track is not None
    assert next_track.title == test_tracks[0].title  # Цикличное воспроизведение

def test_program_schedule(db, test_program):
    """Тест расписания программ"""
    # Получаем расписание тестовой программы
    stmt = select(ProgramSchedule).where(ProgramSchedule.program_id == test_program.id)
    schedule = db.execute(stmt).scalars().first()
    
    assert schedule is not None
    assert schedule.program_id == test_program.id
    assert schedule.repeat_type == "daily"
    
    # Проверяем, что время окончания на 1 час больше времени начала
    time_diff = schedule.end_time - schedule.start_time
    assert time_diff.total_seconds() == 3600  # 1 час = 3600 секунд 