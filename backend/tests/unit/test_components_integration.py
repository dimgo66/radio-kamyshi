"""
Интеграционные тесты для проверки взаимодействия основных компонентов системы
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
from typing import List, Dict, Any, Optional

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
    file_size = Column(Integer, nullable=True)
    format = Column(String, nullable=True)
    bitrate = Column(Integer, nullable=True)
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

# Класс для обработки аудио
class AudioProcessor:
    """
    Класс для обработки аудио файлов
    """
    
    def __init__(self, storage_dir: str = "/tmp"):
        self.storage_dir = storage_dir
        self.allowed_extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Имитация извлечения метаданных из аудио файла
        """
        filename = os.path.basename(file_path).lower()
        
        if "rock" in filename:
            return {
                "title": "Rock Song",
                "artist": "Rock Artist",
                "album": "Rock Album",
                "genre": "Rock",
                "duration": 180.5,
                "file_size": 1024 * 1024 * 5,
                "format": "mp3",
                "bitrate": 320
            }
        elif "pop" in filename:
            return {
                "title": "Pop Song",
                "artist": "Pop Artist",
                "album": "Pop Album",
                "genre": "Pop",
                "duration": 210.75,
                "file_size": 1024 * 1024 * 4,
                "format": "mp3",
                "bitrate": 256
            }
        else:
            return {
                "title": f"Unknown Track ({filename})",
                "artist": "Unknown Artist",
                "album": "Unknown Album",
                "genre": "Unknown",
                "duration": 120.0,
                "file_size": 1024 * 1024 * 3,
                "format": "mp3",
                "bitrate": 192
            }
    
    def format_duration(self, seconds: float) -> str:
        """
        Форматирование длительности в секундах в формат HH:MM:SS
        """
        if seconds < 0:
            seconds = 0
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02}:{secs:02}"
        else:
            return f"{minutes:02}:{secs:02}"
    
    def validate_audio_file(self, file_path: str, max_size_mb: int = 100) -> bool:
        """
        Имитация проверки аудио файла
        """
        file_ext = os.path.splitext(os.path.basename(file_path))[1].lower()
        return file_ext in self.allowed_extensions

# Класс для управления плейлистами
class PlaylistManager:
    def __init__(self, db: Session, audio_processor: AudioProcessor = None):
        self.db = db
        self.audio_processor = audio_processor or AudioProcessor()
    
    def create_playlist(self, name: str, description: str, user_id: int) -> Playlist:
        """
        Создает плейлист
        """
        playlist = Playlist(
            name=name,
            description=description,
            user_id=user_id
        )
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        return playlist
    
    def add_track_to_playlist(self, playlist_id: int, track_id: int, position: int = None) -> PlaylistTrack:
        """
        Добавляет трек в плейлист
        """
        # Если позиция не указана, добавляем в конец
        if position is None:
            # Определяем максимальную позицию
            max_pos = self.db.query(PlaylistTrack.position).filter(
                PlaylistTrack.playlist_id == playlist_id
            ).order_by(PlaylistTrack.position.desc()).first()
            
            position = 1 if max_pos is None else max_pos[0] + 1
        
        playlist_track = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_id,
            position=position
        )
        self.db.add(playlist_track)
        self.db.commit()
        self.db.refresh(playlist_track)
        return playlist_track
    
    def get_playlist_tracks(self, playlist_id: int) -> List[Dict]:
        """
        Получает треки плейлиста
        """
        tracks = self.db.query(Track).join(
            PlaylistTrack, PlaylistTrack.track_id == Track.id
        ).filter(
            PlaylistTrack.playlist_id == playlist_id
        ).all()
        
        result = []
        for track in tracks:
            result.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "genre": track.genre,
                "duration": track.duration,
                "duration_formatted": self.audio_processor.format_duration(track.duration),
                "file_path": track.file_path
            })
        
        return result

# Класс для управления треками
class TrackManager:
    def __init__(self, db: Session, audio_processor: AudioProcessor = None):
        self.db = db
        self.audio_processor = audio_processor or AudioProcessor()
    
    def create_track(self, file_path: str, user_id: int) -> Track:
        """
        Создает трек на основе файла
        """
        if not self.audio_processor.validate_audio_file(file_path):
            raise ValueError(f"Неверный формат файла: {file_path}")
        
        metadata = self.audio_processor.extract_metadata(file_path)
        
        track = Track(
            title=metadata.get("title", os.path.basename(file_path)),
            artist=metadata.get("artist", "Unknown"),
            album=metadata.get("album", "Unknown"),
            genre=metadata.get("genre", "Unknown"),
            file_path=file_path,
            duration=metadata.get("duration", 0.0),
            file_size=metadata.get("file_size", 0),
            format=metadata.get("format", "unknown"),
            bitrate=metadata.get("bitrate", 0),
            user_id=user_id
        )
        
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track
    
    def get_track(self, track_id: int) -> Track:
        """
        Получает трек по ID
        """
        return self.db.query(Track).filter(Track.id == track_id).first()
    
    def search_tracks(self, query: str) -> List[Track]:
        """
        Ищет треки по запросу
        """
        return self.db.query(Track).filter(
            Track.title.contains(query) | 
            Track.artist.contains(query) | 
            Track.album.contains(query) | 
            Track.genre.contains(query)
        ).all()

# Класс для управления вещанием
class BroadcastManager:
    def __init__(self, db: Session):
        self.db = db
        self.current_track = None
        self.current_program = None
        self.is_broadcasting = False
        self.queue = []
    
    def start_broadcast(self) -> bool:
        """
        Запускает вещание
        """
        if self.is_broadcasting:
            return False
            
        self.is_broadcasting = True
        return True
    
    def stop_broadcast(self) -> bool:
        """
        Останавливает вещание
        """
        if not self.is_broadcasting:
            return False
            
        self.is_broadcasting = False
        self.current_track = None
        self.current_program = None
        self.queue = []
        return True
    
    def set_current_track(self, track_id: int) -> bool:
        """
        Устанавливает текущий трек
        """
        track = self.db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return False
            
        self.current_track = track
        return True
    
    def add_to_queue(self, track_id: int) -> bool:
        """
        Добавляет трек в очередь воспроизведения
        """
        track = self.db.query(Track).filter(Track.id == track_id).first()
        if not track:
            return False
            
        self.queue.append(track)
        return True
    
    def get_queue(self) -> List[Dict]:
        """
        Возвращает очередь воспроизведения
        """
        result = []
        for track in self.queue:
            result.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "duration": track.duration
            })
        return result
    
    def set_program(self, program_id: int) -> bool:
        """
        Устанавливает текущую программу и загружает треки из ее плейлиста
        """
        program = self.db.query(Program).filter(Program.id == program_id).first()
        if not program:
            return False
            
        self.current_program = program
        
        # Если у программы есть плейлист, загружаем треки в очередь
        if program.playlist_id:
            tracks = self.db.query(Track).join(
                PlaylistTrack, PlaylistTrack.track_id == Track.id
            ).filter(
                PlaylistTrack.playlist_id == program.playlist_id
            ).all()
            
            self.queue = tracks
            
            # Устанавливаем первый трек как текущий
            if tracks:
                self.current_track = tracks[0]
        
        return True

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
def audio_processor():
    return AudioProcessor()

@pytest.fixture
def playlist_manager(db, audio_processor):
    return PlaylistManager(db, audio_processor)

@pytest.fixture
def track_manager(db, audio_processor):
    return TrackManager(db, audio_processor)

@pytest.fixture
def broadcast_manager(db):
    return BroadcastManager(db)

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_tracks(db, test_user, track_manager):
    tracks = []
    
    file_paths = [
        "/tmp/rock_song.mp3",
        "/tmp/pop_song.mp3",
        "/tmp/unknown_track.mp3"
    ]
    
    for file_path in file_paths:
        track = track_manager.create_track(file_path, test_user.id)
        tracks.append(track)
    
    return tracks

@pytest.fixture
def test_playlist(db, test_user, playlist_manager, test_tracks):
    playlist = playlist_manager.create_playlist(
        name="Test Playlist",
        description="Playlist for testing",
        user_id=test_user.id
    )
    
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_manager.add_track_to_playlist(
            playlist_id=playlist.id,
            track_id=track.id,
            position=i+1
        )
    
    return playlist

@pytest.fixture
def test_program(db, test_user, test_playlist):
    program = Program(
        name="Test Program",
        description="Program for testing",
        duration=60,
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

# Тесты интеграции
def test_track_playlist_integration(track_manager, playlist_manager, test_user):
    """
    Проверяет интеграцию между треками и плейлистами
    """
    # Создаем треки
    track1 = track_manager.create_track("/tmp/rock_song.mp3", test_user.id)
    track2 = track_manager.create_track("/tmp/pop_song.mp3", test_user.id)
    
    # Создаем плейлист
    playlist = playlist_manager.create_playlist(
        name="Integration Test Playlist",
        description="Testing track-playlist integration",
        user_id=test_user.id
    )
    
    # Добавляем треки в плейлист
    playlist_manager.add_track_to_playlist(playlist.id, track1.id, 1)
    playlist_manager.add_track_to_playlist(playlist.id, track2.id, 2)
    
    # Получаем треки из плейлиста
    playlist_tracks = playlist_manager.get_playlist_tracks(playlist.id)
    
    # Проверяем интеграцию
    assert len(playlist_tracks) == 2
    assert playlist_tracks[0]["title"] == "Rock Song"
    assert playlist_tracks[1]["title"] == "Pop Song"

def test_playlist_broadcast_integration(playlist_manager, broadcast_manager, test_user, test_playlist, test_tracks):
    """
    Проверяет интеграцию между плейлистами и вещанием
    """
    # Запускаем вещание
    assert broadcast_manager.start_broadcast() is True
    
    # Устанавливаем текущий трек
    broadcast_manager.set_current_track(test_tracks[0].id)
    
    # Добавляем треки из плейлиста в очередь
    tracks = playlist_manager.get_playlist_tracks(test_playlist.id)
    for track in tracks:
        broadcast_manager.add_to_queue(track["id"])
    
    # Проверяем очередь
    queue = broadcast_manager.get_queue()
    assert len(queue) == 3
    
    # Останавливаем вещание
    assert broadcast_manager.stop_broadcast() is True
    assert broadcast_manager.is_broadcasting is False
    assert broadcast_manager.current_track is None

def test_program_broadcast_integration(broadcast_manager, test_program):
    """
    Проверяет интеграцию между программами и вещанием
    """
    # Запускаем вещание
    assert broadcast_manager.start_broadcast() is True
    
    # Устанавливаем программу
    assert broadcast_manager.set_program(test_program.id) is True
    
    # Проверяем, что треки из плейлиста программы загружены в очередь
    assert broadcast_manager.current_program is not None
    assert broadcast_manager.current_program.id == test_program.id
    
    # Проверяем, что текущий трек установлен на первый трек плейлиста программы
    assert broadcast_manager.current_track is not None
    
    # Проверяем очередь
    queue = broadcast_manager.get_queue()
    assert len(queue) == 3  # Все треки из тестового плейлиста
    
    # Останавливаем вещание
    assert broadcast_manager.stop_broadcast() is True

def test_complete_workflow(track_manager, playlist_manager, broadcast_manager, test_user):
    """
    Проверяет полный рабочий процесс от создания треков до вещания
    """
    # 1. Создаем треки
    track1 = track_manager.create_track("/tmp/rock_song.mp3", test_user.id)
    track2 = track_manager.create_track("/tmp/pop_song.mp3", test_user.id)
    
    # 2. Создаем плейлист
    playlist = playlist_manager.create_playlist(
        name="Workflow Playlist",
        description="Testing complete workflow",
        user_id=test_user.id
    )
    
    # 3. Добавляем треки в плейлист
    playlist_manager.add_track_to_playlist(playlist.id, track1.id, 1)
    playlist_manager.add_track_to_playlist(playlist.id, track2.id, 2)
    
    # 4. Создаем программу с плейлистом
    program = Program(
        name="Workflow Program",
        description="Program for workflow testing",
        duration=30,
        type="music",
        user_id=test_user.id,
        playlist_id=playlist.id
    )
    db = playlist_manager.db
    db.add(program)
    db.commit()
    db.refresh(program)
    
    # 5. Запускаем вещание
    broadcast_manager.start_broadcast()
    
    # 6. Устанавливаем программу
    broadcast_manager.set_program(program.id)
    
    # Проверяем результаты
    assert broadcast_manager.is_broadcasting is True
    assert broadcast_manager.current_program is not None
    assert broadcast_manager.current_program.id == program.id
    assert broadcast_manager.current_track is not None
    assert broadcast_manager.current_track.id == track1.id  # Первый трек в плейлисте
    
    # Проверяем очередь
    queue = broadcast_manager.get_queue()
    assert len(queue) == 2  # Оба трека должны быть в очереди 