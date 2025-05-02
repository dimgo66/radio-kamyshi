"""
Тесты для проверки функциональности плейлистов с треками
"""
import sqlalchemy as sa
import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, and_, func, text
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

# Имитация процессора аудио
class MockAudioProcessor:
    def __init__(self, storage_dir=None):
        self.storage_dir = storage_dir or tempfile.gettempdir()
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Мок для извлечения метаданных"""
        # Определяем метаданные на основе имени файла
        filename = os.path.basename(file_path).lower()
        
        if "rock" in filename:
            return {
                "title": "Rock Song",
                "artist": "Rock Artist",
                "album": "Rock Album",
                "genre": "Rock",
                "duration": 180.5,  # 3:00.5
                "file_size": 1024 * 1024 * 5,  # 5 MB
                "file_name": filename
            }
        elif "pop" in filename:
            return {
                "title": "Pop Song",
                "artist": "Pop Artist",
                "album": "Pop Album",
                "genre": "Pop",
                "duration": 210.75,  # 3:30.75
                "file_size": 1024 * 1024 * 4,  # 4 MB
                "file_name": filename
            }
        elif "jazz" in filename:
            return {
                "title": "Jazz Improvisation",
                "artist": "Jazz Musician",
                "album": "Jazz Collection",
                "genre": "Jazz",
                "duration": 360.25,  # 6:00.25
                "file_size": 1024 * 1024 * 8,  # 8 MB
                "file_name": filename
            }
        else:
            return {
                "title": f"Unknown Track ({filename})",
                "artist": "Unknown Artist",
                "album": "Unknown Album",
                "genre": "Unknown",
                "duration": 120.0,  # 2:00
                "file_size": 1024 * 1024 * 3,  # 3 MB
                "file_name": filename
            }
    
    def format_duration(self, seconds: float) -> str:
        """Мок для форматирования длительности"""
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
        """Мок для валидации аудиофайла"""
        # Проверяем расширение
        ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
        
        # Симулируем проверку размера
        filename = os.path.basename(file_path).lower()
        size_mb = 0
        
        if "rock" in filename:
            size_mb = 5
        elif "pop" in filename:
            size_mb = 4
        elif "jazz" in filename:
            size_mb = 8
        else:
            size_mb = 3
        
        return ext in valid_extensions and size_mb <= max_size_mb
    
    def convert_to_mp3(self, file_path: str, bitrate: int = 320) -> str:
        """Мок для конвертации в MP3"""
        # Просто возвращаем новый путь с расширением .mp3
        filename = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(self.storage_dir, f"{filename}.mp3")

# Класс для управления плейлистами
class PlaylistManager:
    def __init__(self, db: Session, audio_processor: MockAudioProcessor):
        self.db = db
        self.audio_processor = audio_processor
    
    def create_playlist(self, name: str, description: str, user_id: int, is_public: bool = True) -> Playlist:
        """Создание нового плейлиста"""
        playlist = Playlist(
            name=name,
            description=description,
            is_public=is_public,
            user_id=user_id
        )
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        return playlist
    
    def add_track_to_playlist(self, playlist_id: int, track_id: int, position: Optional[int] = None) -> Optional[PlaylistTrack]:
        """Добавление трека в плейлист"""
        # Используем текстовый SQL для надежности
        from sqlalchemy import text
        
        # Проверяем, существует ли плейлист
        result = self.db.execute(text("SELECT * FROM playlists WHERE id = :id"), {"id": playlist_id})
        playlist = result.fetchone()
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Проверяем, существует ли трек
        result = self.db.execute(text("SELECT * FROM tracks WHERE id = :id"), {"id": track_id})
        track = result.fetchone()
        if not track:
            raise ValueError(f"Трек с ID {track_id} не найден")
        
        # Если позиция не указана, добавляем в конец
        if position is None:
            # Определяем максимальную позицию с помощью текстового SQL
            result = self.db.execute(
                text("SELECT MAX(position) as max_pos FROM playlist_tracks WHERE playlist_id = :playlist_id"),
                {"playlist_id": playlist_id}
            )
            max_pos_row = result.fetchone()
            max_pos = max_pos_row[0] if max_pos_row and max_pos_row[0] is not None else 0
            position = max_pos + 1
        
        # Проверяем, есть ли трек уже в плейлисте
        result = self.db.execute(
            text("SELECT * FROM playlist_tracks WHERE playlist_id = :playlist_id AND track_id = :track_id"),
            {"playlist_id": playlist_id, "track_id": track_id}
        )
        existing = result.fetchone()
        
        if existing:
            # Если трек уже есть, обновляем его позицию с помощью текстового SQL
            self.db.execute(
                text("UPDATE playlist_tracks SET position = :position WHERE id = :id"),
                {"position": position, "id": existing.id}
            )
            self.db.commit()
            
            # Получаем обновленную запись
            result = self.db.execute(
                text("SELECT * FROM playlist_tracks WHERE id = :id"),
                {"id": existing.id}
            )
            updated = result.fetchone()
            
            # Проверяем обновленную запись
            if updated is None:
                return None
                
            # Возвращаем объект PlaylistTrack
            playlist_track = self.db.query(PlaylistTrack).get(updated.id)
            if playlist_track is not None:
                return playlist_track
                
            # Если не удалось получить объект, создаем новый
            return PlaylistTrack(
                id=updated.id,
                playlist_id=updated.playlist_id,
                track_id=updated.track_id,
                position=updated.position
            )
        
        # Иначе добавляем новую запись
        playlist_track = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_id,
            position=position
        )
        self.db.add(playlist_track)
        self.db.commit()
        self.db.refresh(playlist_track)
        return playlist_track
    
    def remove_track_from_playlist(self, playlist_id: int, track_id: int) -> bool:
        """Удаление трека из плейлиста"""
        from sqlalchemy import text
        
        # Используем текстовый SQL вместо ORM для обхода проблем с типизацией
        result = self.db.execute(
            text("SELECT * FROM playlist_tracks WHERE playlist_id = :playlist_id AND track_id = :track_id"),
            {"playlist_id": playlist_id, "track_id": track_id}
        )
        playlist_track = result.fetchone()
        
        if not playlist_track:
            return False
        
        # Удаляем запись SQL запросом
        self.db.execute(
            text("DELETE FROM playlist_tracks WHERE id = :id"),
            {"id": playlist_track.id}
        )
        self.db.commit()
        return True
    
    def get_playlist_tracks(self, playlist_id: int) -> List[Dict[str, Any]]:
        """Получение треков плейлиста с метаданными"""
        from sqlalchemy import text
        
        # Проверяем, существует ли плейлист
        result = self.db.execute(text("SELECT * FROM playlists WHERE id = :id"), {"id": playlist_id})
        playlist = result.fetchone()
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Получаем треки с помощью SQL вместо ORM
        result = self.db.execute(text("""
            SELECT t.*, pt.position
            FROM tracks t
            JOIN playlist_tracks pt ON t.id = pt.track_id
            WHERE pt.playlist_id = :playlist_id
            ORDER BY pt.position ASC
        """), {"playlist_id": playlist_id})
        
        tracks = result.fetchall()
        
        result = []
        for track in tracks:
            # Безопасно получаем duration
            duration_value = 0
            if track.duration is not None:
                try:
                    duration_value = float(track.duration)
                except (ValueError, TypeError):
                    duration_value = 0
                    
            result.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "genre": track.genre,
                "duration": track.duration,
                "duration_formatted": self.audio_processor.format_duration(duration_value),
                "position": track.position,
                "file_path": track.file_path,
            })
        
        return result
    
    def get_playlist_info(self, playlist_id: int) -> Dict[str, Any]:
        """Получение информации о плейлисте"""
        from sqlalchemy import text
        
        # Получаем плейлист прямым SQL запросом
        result = self.db.execute(text("SELECT * FROM playlists WHERE id = :id"), {"id": playlist_id})
        playlist = result.fetchone()
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Получаем количество треков
        result = self.db.execute(
            text("SELECT COUNT(*) as count FROM playlist_tracks WHERE playlist_id = :playlist_id"),
            {"playlist_id": playlist_id}
        )
        track_count = result.scalar() or 0
        
        # Получаем общую длительность через SQL
        result = self.db.execute(text("""
            SELECT SUM(t.duration) as total_duration
            FROM tracks t
            JOIN playlist_tracks pt ON t.id = pt.track_id
            WHERE pt.playlist_id = :playlist_id
        """), {"playlist_id": playlist_id})
        
        total_duration = result.scalar() or 0
        total_duration_seconds = float(total_duration)
        
        return {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "is_public": playlist.is_public,
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at,
            "user_id": playlist.user_id,
            "track_count": track_count,
            "total_duration": total_duration_seconds,
            "total_duration_formatted": self.audio_processor.format_duration(total_duration_seconds)
        }
    
    def update_playlist(self, playlist_id: int, data: Dict[str, Any]) -> Playlist:
        """Обновление информации о плейлисте"""
        playlist = self.db.query(Playlist).first()
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Обновляем поля
        for key, value in data.items():
            if hasattr(playlist, key):
                setattr(playlist, key, value)
        
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        return playlist
    
    def reorder_tracks(self, playlist_id: int, track_order: List[Dict[str, int]]) -> bool:
        """Изменение порядка треков в плейлисте"""
        from sqlalchemy import text
        
        # Проверяем, существует ли плейлист
        result = self.db.execute(text("SELECT * FROM playlists WHERE id = :id"), {"id": playlist_id})
        playlist = result.fetchone()
        
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Обновляем позиции
        for item in track_order:
            track_id = item.get("track_id")
            position = item.get("position")
            
            if track_id is None or position is None:
                continue
            
            # Обновляем позицию через текстовый SQL запрос
            self.db.execute(
                text("""
                    UPDATE playlist_tracks 
                    SET position = :position 
                    WHERE playlist_id = :playlist_id AND track_id = :track_id
                """),
                {"position": position, "playlist_id": playlist_id, "track_id": track_id}
            )
        
        self.db.commit()
        return True

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
def audio_processor():
    """Фикстура для аудио процессора"""
    return MockAudioProcessor()

@pytest.fixture
def playlist_manager(db, audio_processor):
    """Фикстура для менеджера плейлистов"""
    return PlaylistManager(db, audio_processor)

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
def test_playlist(db, test_user):
    """Фикстура для создания тестового плейлиста"""
    playlist = Playlist(
        name="Test Playlist",
        description="Playlist for testing",
        is_public=True,
        user_id=test_user.id
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist

# Тесты
def test_create_playlist(playlist_manager, test_user):
    """Тест создания плейлиста"""
    playlist = playlist_manager.create_playlist(
        name="New Playlist",
        description="A newly created playlist",
        user_id=test_user.id,
        is_public=True
    )
    
    assert playlist.id is not None
    assert playlist.name == "New Playlist"
    assert playlist.description == "A newly created playlist"
    assert playlist.user_id == test_user.id
    assert playlist.is_public is True

def test_add_track_to_playlist(playlist_manager, test_playlist, test_tracks):
    """Тест добавления трека в плейлист"""
    track = test_tracks[0]
    
    # Добавляем трек в плейлист
    playlist_track = playlist_manager.add_track_to_playlist(
        playlist_id=test_playlist.id,
        track_id=track.id,
        position=1
    )
    
    assert playlist_track.id is not None
    assert playlist_track.playlist_id == test_playlist.id
    assert playlist_track.track_id == track.id
    assert playlist_track.position == 1
    
    # Добавляем второй трек без указания позиции
    track2 = test_tracks[1]
    playlist_track2 = playlist_manager.add_track_to_playlist(
        playlist_id=test_playlist.id,
        track_id=track2.id
    )
    
    assert playlist_track2.position == 2  # Должна быть вычислена автоматически

def test_get_playlist_tracks(playlist_manager, test_playlist, test_tracks):
    """Тест получения треков плейлиста"""
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_manager.add_track_to_playlist(
            playlist_id=test_playlist.id,
            track_id=track.id,
            position=i+1
        )
    
    # Получаем треки
    tracks = playlist_manager.get_playlist_tracks(test_playlist.id)
    
    assert len(tracks) == len(test_tracks)
    assert tracks[0]["title"] == "Rock Song"
    assert tracks[1]["title"] == "Pop Song"
    assert tracks[2]["title"] == "Jazz Improvisation"
    
    # Проверяем форматирование длительности
    assert tracks[0]["duration_formatted"] == "03:00"
    assert tracks[1]["duration_formatted"] == "03:30"
    assert tracks[2]["duration_formatted"] == "06:00"

def test_get_playlist_info(playlist_manager, test_playlist, test_tracks):
    """Тест получения информации о плейлисте"""
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_manager.add_track_to_playlist(
            playlist_id=test_playlist.id,
            track_id=track.id,
            position=i+1
        )
    
    # Получаем информацию о плейлисте
    info = playlist_manager.get_playlist_info(test_playlist.id)
    
    assert info["name"] == "Test Playlist"
    assert info["description"] == "Playlist for testing"
    assert info["track_count"] == 3
    
    # Проверяем, что общая длительность правильно вычислена и отформатирована
    # Сумма: 180.5 + 210.75 + 360.25 = 751.5 секунд = 12:31.5
    expected_duration = 751.5
    assert abs(info["total_duration"] - expected_duration) < 0.01
    assert info["total_duration_formatted"] == "12:31"

def test_update_playlist(playlist_manager, test_playlist):
    """Тест обновления информации о плейлисте"""
    updated = playlist_manager.update_playlist(
        playlist_id=test_playlist.id,
        data={
            "name": "Updated Playlist Name",
            "description": "Updated description",
            "is_public": False
        }
    )
    
    assert updated.name == "Updated Playlist Name"
    assert updated.description == "Updated description"
    assert updated.is_public is False

def test_remove_track_from_playlist(playlist_manager, test_playlist, test_tracks):
    """Тест удаления трека из плейлиста"""
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_manager.add_track_to_playlist(
            playlist_id=test_playlist.id,
            track_id=track.id,
            position=i+1
        )
    
    # Удаляем второй трек
    result = playlist_manager.remove_track_from_playlist(
        playlist_id=test_playlist.id,
        track_id=test_tracks[1].id
    )
    
    assert result is True
    
    # Проверяем, что трек удален
    tracks = playlist_manager.get_playlist_tracks(test_playlist.id)
    assert len(tracks) == 2
    assert tracks[0]["title"] == "Rock Song"
    assert tracks[1]["title"] == "Jazz Improvisation"

def test_reorder_tracks(playlist_manager, test_playlist, test_tracks):
    """Тест изменения порядка треков в плейлисте"""
    # Добавляем треки в плейлист
    for i, track in enumerate(test_tracks):
        playlist_manager.add_track_to_playlist(
            playlist_id=test_playlist.id,
            track_id=track.id,
            position=i+1
        )
    
    # Меняем порядок (обратный порядок)
    new_order = [
        {"track_id": test_tracks[2].id, "position": 1},
        {"track_id": test_tracks[1].id, "position": 2},
        {"track_id": test_tracks[0].id, "position": 3}
    ]
    
    result = playlist_manager.reorder_tracks(test_playlist.id, new_order)
    assert result is True
    
    # Проверяем новый порядок
    tracks = playlist_manager.get_playlist_tracks(test_playlist.id)
    assert tracks[0]["title"] == "Jazz Improvisation"
    assert tracks[1]["title"] == "Pop Song"
    assert tracks[2]["title"] == "Rock Song" 