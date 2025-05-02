"""
Интеграционные тесты для модулей обработки аудио и плейлистов
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
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
    file_size = Column(Integer)
    format = Column(String)
    bitrate = Column(Integer)
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

# Класс для обработки аудио
class AudioProcessor:
    """
    Класс для обработки аудио файлов
    """
    
    def __init__(self, storage_dir: str = "/tmp"):
        """
        Инициализация процессора аудио
        
        Args:
            storage_dir: Директория для хранения аудио файлов
        """
        self.storage_dir = storage_dir
        self.allowed_extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Извлечение метаданных из аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            
        Returns:
            Словарь с метаданными
        """
        # Имитация извлечения метаданных (в тестах)
        filename = os.path.basename(file_path).lower()
        
        if "rock" in filename:
            return {
                "title": "Rock Song",
                "artist": "Rock Artist",
                "album": "Rock Album",
                "genre": "Rock",
                "duration": 180.5,  # 3:00.5
                "file_size": 1024 * 1024 * 5,  # 5 MB
                "file_name": filename,
                "format": "mp3",
                "bitrate": 320
            }
        elif "pop" in filename:
            return {
                "title": "Pop Song",
                "artist": "Pop Artist",
                "album": "Pop Album",
                "genre": "Pop",
                "duration": 210.75,  # 3:30.75
                "file_size": 1024 * 1024 * 4,  # 4 MB
                "file_name": filename,
                "format": "mp3",
                "bitrate": 256
            }
        elif "jazz" in filename:
            return {
                "title": "Jazz Improvisation",
                "artist": "Jazz Musician",
                "album": "Jazz Collection",
                "genre": "Jazz",
                "duration": 360.25,  # 6:00.25
                "file_size": 1024 * 1024 * 8,  # 8 MB
                "file_name": filename,
                "format": "flac",
                "bitrate": 1411
            }
        else:
            return {
                "title": f"Unknown Track ({filename})",
                "artist": "Unknown Artist",
                "album": "Unknown Album",
                "genre": "Unknown",
                "duration": 120.0,  # 2:00
                "file_size": 1024 * 1024 * 3,  # 3 MB
                "file_name": filename,
                "format": "mp3",
                "bitrate": 192
            }
    
    def format_duration(self, seconds: float) -> str:
        """
        Форматирование длительности в секундах в формат HH:MM:SS
        
        Args:
            seconds: Длительность в секундах
            
        Returns:
            Отформатированная строка времени
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
        Проверка аудио файла на корректность
        
        Args:
            file_path: Путь к аудио файлу
            max_size_mb: Максимальный размер файла в МБ
            
        Returns:
            True если файл корректный, иначе False
        """
        # Проверяем расширение
        file_ext = os.path.splitext(os.path.basename(file_path))[1].lower()
        if file_ext not in self.allowed_extensions:
            return False
        
        # Имитация проверки размера файла (в тестах)
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
        
        return size_mb <= max_size_mb
    
    def convert_to_mp3(self, file_path: str, bitrate: int = 320) -> str:
        """
        Имитация конвертации аудио файла в MP3
        
        Args:
            file_path: Путь к аудио файлу
            bitrate: Битрейт для MP3 (кбит/с)
            
        Returns:
            Путь к сконвертированному MP3 файлу
        """
        # Просто возвращаем новый путь с расширением .mp3
        filename = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(self.storage_dir, f"{filename}.mp3")
    
    def generate_waveform(self, file_path: str, pixels_per_second: int = 10) -> Dict[str, Any]:
        """
        Имитация генерации данных о форме волны аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            pixels_per_second: Количество точек на секунду
            
        Returns:
            Словарь с данными формы волны
        """
        # Получаем метаданные для определения длительности
        metadata = self.extract_metadata(file_path)
        duration = metadata.get("duration", 0)
        
        # Генерируем случайные данные для формы волны
        num_points = int(duration * pixels_per_second)
        data = [i % 100 for i in range(num_points)]  # Просто последовательность для теста
        
        return {
            "data": data,
            "sample_rate": 44100,
            "channels": 2,
            "duration": duration
        }

# Класс для управления плейлистами с интеграцией обработки аудио
class PlaylistAudioManager:
    def __init__(self, db: Session, audio_processor: AudioProcessor):
        self.db = db
        self.audio_processor = audio_processor
    
    def create_track_from_file(self, file_path: str, user_id: int) -> Track:
        """
        Создает запись трека в БД на основе аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            user_id: ID пользователя
            
        Returns:
            Объект Track
        """
        # Проверяем файл
        if not self.audio_processor.validate_audio_file(file_path):
            raise ValueError(f"Файл {file_path} не является допустимым аудио файлом")
        
        # Извлекаем метаданные
        metadata = self.audio_processor.extract_metadata(file_path)
        
        # Создаем трек
        track = Track(
            title=metadata.get("title", "Unknown"),
            artist=metadata.get("artist", "Unknown"),
            album=metadata.get("album", "Unknown"),
            genre=metadata.get("genre", "Unknown"),
            file_path=file_path,
            duration=metadata.get("duration", 0.0),
            file_size=metadata.get("file_size", 0),
            format=metadata.get("format", "mp3"),
            bitrate=metadata.get("bitrate", 192),
            user_id=user_id
        )
        
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track
    
    def create_playlist_with_tracks(self, name: str, description: str, 
                                   file_paths: List[str], user_id: int) -> Playlist:
        """
        Создает плейлист и добавляет в него треки из файлов
        
        Args:
            name: Название плейлиста
            description: Описание плейлиста
            file_paths: Список путей к аудио файлам
            user_id: ID пользователя
            
        Returns:
            Объект Playlist
        """
        # Создаем плейлист
        playlist = Playlist(
            name=name,
            description=description,
            user_id=user_id
        )
        
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        
        # Добавляем треки в плейлист
        for i, file_path in enumerate(file_paths):
            try:
                # Проверяем, существует ли трек с таким путем
                track = self.db.query(Track).filter(Track.file_path == file_path).first()
                
                # Если трека нет, создаем его
                if not track:
                    track = self.create_track_from_file(file_path, user_id)
                
                # Добавляем трек в плейлист
                playlist_track = PlaylistTrack(
                    playlist_id=playlist.id,
                    track_id=track.id,
                    position=i+1
                )
                
                self.db.add(playlist_track)
            except Exception as e:
                print(f"Ошибка при добавлении трека {file_path}: {e}")
        
        self.db.commit()
        return playlist
    
    def get_playlist_duration(self, playlist_id: int) -> Dict[str, Any]:
        """
        Получает общую длительность плейлиста и форматирует ее
        
        Args:
            playlist_id: ID плейлиста
            
        Returns:
            Словарь с информацией о длительности
        """
        # Получаем общую длительность треков в плейлисте
        total_duration = self.db.query(Track).join(
            PlaylistTrack
        ).filter(
            PlaylistTrack.playlist_id == playlist_id
        ).with_entities(
            Track.duration
        ).all()
        
        # Суммируем длительности
        total_seconds = sum([duration[0] for duration in total_duration])
        
        # Форматируем длительность
        formatted_duration = self.audio_processor.format_duration(total_seconds)
        
        return {
            "total_seconds": total_seconds,
            "formatted_duration": formatted_duration
        }
    
    def get_playlist_with_tracks(self, playlist_id: int) -> Dict[str, Any]:
        """
        Получает плейлист с треками и их метаданными
        
        Args:
            playlist_id: ID плейлиста
            
        Returns:
            Словарь с информацией о плейлисте и треках
        """
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        
        if not playlist:
            raise ValueError(f"Плейлист с ID {playlist_id} не найден")
        
        # Получаем треки
        tracks_query = self.db.query(
            Track, PlaylistTrack.position
        ).join(
            PlaylistTrack
        ).filter(
            PlaylistTrack.playlist_id == playlist_id
        ).order_by(
            PlaylistTrack.position
        ).all()
        
        tracks = []
        for track, position in tracks_query:
            tracks.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "genre": track.genre,
                "duration": track.duration,
                "duration_formatted": self.audio_processor.format_duration(track.duration),
                "format": track.format,
                "bitrate": track.bitrate,
                "position": position
            })
        
        # Получаем общую длительность
        duration_info = self.get_playlist_duration(playlist_id)
        
        return {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "user_id": playlist.user_id,
            "tracks_count": len(tracks),
            "total_duration": duration_info["total_seconds"],
            "total_duration_formatted": duration_info["formatted_duration"],
            "tracks": tracks
        }

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
    """Фикстура для аудио процессора"""
    return AudioProcessor()

@pytest.fixture
def playlist_audio_manager(db, audio_processor):
    """Фикстура для менеджера плейлистов с интеграцией аудио"""
    return PlaylistAudioManager(db, audio_processor)

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
def test_audio_files():
    """Фикстура с тестовыми путями к аудио файлам"""
    return [
        "/tmp/rock_song.mp3",
        "/tmp/pop_song.mp3",
        "/tmp/jazz_track.flac",
        "/tmp/unknown_track.mp3"
    ]

# Тесты
def test_create_track_from_file(playlist_audio_manager, test_user, test_audio_files):
    """Тест создания трека из аудио файла"""
    file_path = test_audio_files[0]  # rock_song.mp3
    
    track = playlist_audio_manager.create_track_from_file(file_path, test_user.id)
    
    assert track.id is not None
    assert track.title == "Rock Song"
    assert track.artist == "Rock Artist"
    assert track.album == "Rock Album"
    assert track.genre == "Rock"
    assert track.duration == 180.5
    assert track.file_path == file_path
    assert track.user_id == test_user.id

def test_create_playlist_with_tracks(playlist_audio_manager, test_user, test_audio_files):
    """Тест создания плейлиста с треками из аудио файлов"""
    playlist = playlist_audio_manager.create_playlist_with_tracks(
        name="Test Audio Playlist",
        description="Playlist created from audio files",
        file_paths=test_audio_files,
        user_id=test_user.id
    )
    
    assert playlist.id is not None
    assert playlist.name == "Test Audio Playlist"
    assert playlist.description == "Playlist created from audio files"
    
    # Проверяем, что треки созданы и добавлены в плейлист
    playlist_info = playlist_audio_manager.get_playlist_with_tracks(playlist.id)
    assert playlist_info["tracks_count"] == 4
    
    # Проверяем треки
    tracks = playlist_info["tracks"]
    
    assert tracks[0]["title"] == "Rock Song"
    assert tracks[0]["artist"] == "Rock Artist"
    assert tracks[0]["duration_formatted"] == "03:00"
    
    assert tracks[1]["title"] == "Pop Song"
    assert tracks[1]["artist"] == "Pop Artist"
    assert tracks[1]["duration_formatted"] == "03:30"
    
    assert tracks[2]["title"] == "Jazz Improvisation"
    assert tracks[2]["artist"] == "Jazz Musician"
    assert tracks[2]["duration_formatted"] == "06:00"

def test_get_playlist_duration(playlist_audio_manager, test_user, test_audio_files):
    """Тест получения общей длительности плейлиста"""
    playlist = playlist_audio_manager.create_playlist_with_tracks(
        name="Duration Test Playlist",
        description="Playlist for testing duration calculation",
        file_paths=test_audio_files[:3],  # Только первые три файла
        user_id=test_user.id
    )
    
    duration_info = playlist_audio_manager.get_playlist_duration(playlist.id)
    
    # Сумма длительностей: 180.5 + 210.75 + 360.25 = 751.5 секунд = 12:31.5
    assert abs(duration_info["total_seconds"] - 751.5) < 0.01
    assert duration_info["formatted_duration"] == "12:31"

def test_validate_audio_files(playlist_audio_manager, audio_processor):
    """Тест валидации аудио файлов"""
    # Корректные файлы
    assert audio_processor.validate_audio_file("/tmp/test.mp3") is True
    assert audio_processor.validate_audio_file("/tmp/test.wav") is True
    assert audio_processor.validate_audio_file("/tmp/test.flac") is True
    
    # Некорректные файлы
    assert audio_processor.validate_audio_file("/tmp/test.txt") is False
    assert audio_processor.validate_audio_file("/tmp/test.jpg") is False
    
    # Проверка размера (файл jazz больше 5 МБ)
    assert audio_processor.validate_audio_file("/tmp/jazz_track.flac", max_size_mb=5) is False

def test_waveform_generation(audio_processor, test_audio_files):
    """Тест генерации данных о форме волны"""
    file_path = test_audio_files[0]  # rock_song.mp3
    
    waveform = audio_processor.generate_waveform(file_path)
    
    assert waveform is not None
    assert "data" in waveform
    assert "sample_rate" in waveform
    assert "channels" in waveform
    assert "duration" in waveform
    
    # Проверяем, что длина данных соответствует длительности и частоте сэмплирования
    expected_points = int(180.5 * 10)  # 180.5 секунд * 10 точек/сек
    assert len(waveform["data"]) == expected_points 