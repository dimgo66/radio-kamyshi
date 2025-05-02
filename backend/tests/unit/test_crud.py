"""
Тесты для CRUD операций
"""
import pytest
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import enum
from datetime import datetime, timedelta

# Создаем базовый класс модели
Base = declarative_base()

# Определяем перечисления
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
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    year = Column(Integer)
    file_path = Column(String, nullable=False)
    duration = Column(Float)
    file_size = Column(Integer)
    format = Column(String)
    bitrate = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="tracks")

User.tracks = relationship("Track", back_populates="user")

class Playlist(Base):
    __tablename__ = "playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="playlists")
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist")

User.playlists = relationship("Playlist", back_populates="user")

class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    track_id = Column(Integer, ForeignKey("tracks.id"))
    position = Column(Integer)
    
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track")

# CRUD классы
class CRUDBase:
    def __init__(self, model):
        self.model = model
        
    def get(self, db, id):
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db, skip=0, limit=100):
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db, obj_in):
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        # Отфильтровываем None значения
        filtered_data = {k: v for k, v in obj_data.items() if v is not None}
        db_obj = self.model(**filtered_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db, db_obj, obj_in):
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        for field in update_data:
            if hasattr(db_obj, field) and update_data[field] is not None:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db, id):
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj

class CRUDUser(CRUDBase):
    def get_by_email(self, db, email):
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db, username):
        return db.query(User).filter(User.username == username).first()

class CRUDTrack(CRUDBase):
    def get_by_user(self, db, user_id, skip=0, limit=100):
        return db.query(Track).filter(Track.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_title(self, db, title, skip=0, limit=100):
        return db.query(Track).filter(Track.title.ilike(f"%{title}%")).offset(skip).limit(limit).all()
    
    def get_by_artist(self, db, artist, skip=0, limit=100):
        return db.query(Track).filter(Track.artist.ilike(f"%{artist}%")).offset(skip).limit(limit).all()

class CRUDPlaylist(CRUDBase):
    def get_by_user(self, db, user_id, skip=0, limit=100):
        return db.query(Playlist).filter(Playlist.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_tracks(self, db, playlist_id):
        playlist_tracks = db.query(PlaylistTrack).filter(
            PlaylistTrack.playlist_id == playlist_id
        ).order_by(PlaylistTrack.position).all()
        
        return [pt.track for pt in playlist_tracks]
    
    def add_track(self, db, playlist_id, track_id, position=None):
        # Если позиция не указана, добавляем в конец
        if position is None:
            last_position = db.query(PlaylistTrack).filter(
                PlaylistTrack.playlist_id == playlist_id
            ).count()
            position = last_position + 1
        
        playlist_track = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_id,
            position=position
        )
        db.add(playlist_track)
        db.commit()
        db.refresh(playlist_track)
        return playlist_track
    
    def remove_track(self, db, playlist_id, track_id):
        playlist_track = db.query(PlaylistTrack).filter(
            PlaylistTrack.playlist_id == playlist_id,
            PlaylistTrack.track_id == track_id
        ).first()
        
        db.delete(playlist_track)
        db.commit()
        return playlist_track

# Создаем экземпляры CRUD классов
crud_user = CRUDUser(User)
crud_track = CRUDTrack(Track)
crud_playlist = CRUDPlaylist(Playlist)

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

# Тесты
def test_crud_user(db):
    """Тест CRUD операций для пользователя"""
    # Создание пользователя
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashedpassword",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_superuser": False
    }
    user = crud_user.create(db, user_data)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    
    # Получение пользователя
    retrieved_user = crud_user.get(db, user.id)
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email
    
    # Получение пользователя по email
    email_user = crud_user.get_by_email(db, "test@example.com")
    assert email_user.id == user.id
    
    # Получение пользователя по username
    username_user = crud_user.get_by_username(db, "testuser")
    assert username_user.id == user.id
    
    # Обновление пользователя
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    updated_user = crud_user.update(db, user, update_data)
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Name"
    assert updated_user.email == "test@example.com"  # Неизмененные поля
    
    # Удаление пользователя
    deleted_user = crud_user.remove(db, user.id)
    assert deleted_user.id == user.id
    
    # Проверка, что пользователь удален
    assert crud_user.get(db, user.id) is None

def test_crud_track(db):
    """Тест CRUD операций для треков"""
    # Создаем пользователя
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashedpassword"
    }
    user = crud_user.create(db, user_data)
    
    # Создаем трек
    track_data = {
        "title": "Test Track",
        "artist": "Test Artist",
        "album": "Test Album",
        "genre": "Rock",
        "year": 2023,
        "file_path": "/path/to/file.mp3",
        "duration": 180.5,
        "file_size": 1024000,
        "format": "mp3",
        "bitrate": 320,
        "user_id": user.id
    }
    track = crud_track.create(db, track_data)
    
    assert track.id is not None
    assert track.title == "Test Track"
    assert track.artist == "Test Artist"
    
    # Получение трека
    retrieved_track = crud_track.get(db, track.id)
    assert retrieved_track.id == track.id
    assert retrieved_track.title == track.title
    
    # Получение треков пользователя
    user_tracks = crud_track.get_by_user(db, user.id)
    assert len(user_tracks) == 1
    assert user_tracks[0].id == track.id
    
    # Получение треков по названию
    title_tracks = crud_track.get_by_title(db, "Test")
    assert len(title_tracks) == 1
    assert title_tracks[0].id == track.id
    
    # Получение треков по исполнителю
    artist_tracks = crud_track.get_by_artist(db, "Test")
    assert len(artist_tracks) == 1
    assert artist_tracks[0].id == track.id
    
    # Обновление трека
    update_data = {
        "title": "Updated Track",
        "artist": "Updated Artist"
    }
    updated_track = crud_track.update(db, track, update_data)
    assert updated_track.title == "Updated Track"
    assert updated_track.artist == "Updated Artist"
    assert updated_track.album == "Test Album"  # Неизмененные поля
    
    # Удаление трека
    deleted_track = crud_track.remove(db, track.id)
    assert deleted_track.id == track.id
    
    # Проверка, что трек удален
    assert crud_track.get(db, track.id) is None

def test_crud_playlist(db):
    """Тест CRUD операций для плейлистов"""
    # Создаем пользователя
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashedpassword"
    }
    user = crud_user.create(db, user_data)
    
    # Создаем плейлист
    playlist_data = {
        "name": "Test Playlist",
        "description": "Test playlist description",
        "user_id": user.id
    }
    playlist = crud_playlist.create(db, playlist_data)
    
    assert playlist.id is not None
    assert playlist.name == "Test Playlist"
    assert playlist.description == "Test playlist description"
    
    # Получение плейлиста
    retrieved_playlist = crud_playlist.get(db, playlist.id)
    assert retrieved_playlist.id == playlist.id
    assert retrieved_playlist.name == playlist.name
    
    # Получение плейлистов пользователя
    user_playlists = crud_playlist.get_by_user(db, user.id)
    assert len(user_playlists) == 1
    assert user_playlists[0].id == playlist.id
    
    # Обновление плейлиста
    update_data = {
        "name": "Updated Playlist",
        "description": "Updated description"
    }
    updated_playlist = crud_playlist.update(db, playlist, update_data)
    assert updated_playlist.name == "Updated Playlist"
    assert updated_playlist.description == "Updated description"
    
    # Создаем треки для добавления в плейлист
    track1_data = {
        "title": "Track 1",
        "artist": "Artist 1",
        "file_path": "/path/to/file1.mp3",
        "duration": 180.0,
        "user_id": user.id
    }
    track2_data = {
        "title": "Track 2",
        "artist": "Artist 2",
        "file_path": "/path/to/file2.mp3",
        "duration": 240.0,
        "user_id": user.id
    }
    track1 = crud_track.create(db, track1_data)
    track2 = crud_track.create(db, track2_data)
    
    # Добавляем треки в плейлист
    playlist_track1 = crud_playlist.add_track(db, playlist.id, track1.id)
    playlist_track2 = crud_playlist.add_track(db, playlist.id, track2.id)
    
    assert playlist_track1.playlist_id == playlist.id
    assert playlist_track1.track_id == track1.id
    assert playlist_track1.position == 1
    
    assert playlist_track2.playlist_id == playlist.id
    assert playlist_track2.track_id == track2.id
    assert playlist_track2.position == 2
    
    # Получаем треки из плейлиста
    playlist_tracks = crud_playlist.get_tracks(db, playlist.id)
    assert len(playlist_tracks) == 2
    assert playlist_tracks[0].id == track1.id
    assert playlist_tracks[1].id == track2.id
    
    # Удаляем трек из плейлиста
    removed_playlist_track = crud_playlist.remove_track(db, playlist.id, track1.id)
    assert removed_playlist_track.playlist_id == playlist.id
    assert removed_playlist_track.track_id == track1.id
    
    # Проверяем, что трек удален из плейлиста
    playlist_tracks = crud_playlist.get_tracks(db, playlist.id)
    assert len(playlist_tracks) == 1
    assert playlist_tracks[0].id == track2.id
    
    # Удаление плейлиста
    deleted_playlist = crud_playlist.remove(db, playlist.id)
    assert deleted_playlist.id == playlist.id
    
    # Проверка, что плейлист удален
    assert crud_playlist.get(db, playlist.id) is None 