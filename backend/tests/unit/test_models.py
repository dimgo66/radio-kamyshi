"""
Тесты для моделей данных
"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.track import Track
from app.models.playlist import Playlist, PlaylistTrack
from app.models.program import Program, ProgramSchedule, ProgramType, RepeatType


def test_user_model(db):
    """Тест создания пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    
    # Получаем пользователя из БД
    queried_user = db.query(User).filter(User.email == "test@example.com").first()
    
    assert queried_user is not None
    assert queried_user.email == "test@example.com"
    assert queried_user.username == "testuser"
    assert queried_user.is_active is True
    assert queried_user.is_superuser is False


def test_user_unique_email(db):
    """Тест на уникальность email пользователя"""
    user1 = User(
        email="test@example.com",
        username="testuser1",
        hashed_password="hashedpassword",
    )
    db.add(user1)
    db.commit()
    
    # Пробуем создать пользователя с тем же email
    user2 = User(
        email="test@example.com",
        username="testuser2",
        hashed_password="hashedpassword",
    )
    db.add(user2)
    
    # Должна возникнуть ошибка IntegrityError из-за нарушения ограничения уникальности
    with pytest.raises(IntegrityError):
        db.commit()


def test_track_model(db):
    """Тест создания трека"""
    # Сначала создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    db.commit()
    
    # Создаем трек
    track = Track(
        title="Test Track",
        artist="Test Artist",
        album="Test Album",
        genre="Rock",
        year=2023,
        file_path="/path/to/file.mp3",
        duration=180.5,
        file_size=1024000,
        format="mp3",
        bitrate=320,
        user_id=user.id
    )
    db.add(track)
    db.commit()
    
    # Получаем трек из БД
    queried_track = db.query(Track).filter(Track.title == "Test Track").first()
    
    assert queried_track is not None
    assert queried_track.title == "Test Track"
    assert queried_track.artist == "Test Artist"
    assert queried_track.duration == 180.5
    assert queried_track.user_id == user.id


def test_playlist_model(db):
    """Тест создания плейлиста"""
    # Сначала создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    db.commit()
    
    # Создаем плейлист
    playlist = Playlist(
        name="Test Playlist",
        description="Test Description",
        user_id=user.id
    )
    db.add(playlist)
    db.commit()
    
    # Получаем плейлист из БД
    queried_playlist = db.query(Playlist).filter(Playlist.name == "Test Playlist").first()
    
    assert queried_playlist is not None
    assert queried_playlist.name == "Test Playlist"
    assert queried_playlist.description == "Test Description"
    assert queried_playlist.user_id == user.id


def test_playlist_track_model(db):
    """Тест создания связи плейлиста и трека"""
    # Создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    db.commit()
    
    # Создаем плейлист
    playlist = Playlist(
        name="Test Playlist",
        description="Test Description",
        user_id=user.id
    )
    db.add(playlist)
    
    # Создаем трек
    track = Track(
        title="Test Track",
        artist="Test Artist",
        file_path="/path/to/file.mp3",
        duration=180.5,
        user_id=user.id
    )
    db.add(track)
    db.commit()
    
    # Создаем связь между плейлистом и треком
    playlist_track = PlaylistTrack(
        playlist_id=playlist.id,
        track_id=track.id,
        position=1
    )
    db.add(playlist_track)
    db.commit()
    
    # Получаем связь из БД
    queried_playlist_track = db.query(PlaylistTrack).filter(
        PlaylistTrack.playlist_id == playlist.id,
        PlaylistTrack.track_id == track.id
    ).first()
    
    assert queried_playlist_track is not None
    assert queried_playlist_track.playlist_id == playlist.id
    assert queried_playlist_track.track_id == track.id
    assert queried_playlist_track.position == 1


def test_program_model(db):
    """Тест создания программы"""
    # Создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    
    # Создаем плейлист
    playlist = Playlist(
        name="Test Playlist",
        description="Test Description",
        user_id=user.id
    )
    db.add(playlist)
    db.commit()
    
    # Создаем программу
    program = Program(
        name="Test Program",
        description="Test Program Description",
        duration=60,  # 60 минут
        type=ProgramType.MUSIC,
        playlist_id=playlist.id,
        user_id=user.id
    )
    db.add(program)
    db.commit()
    
    # Получаем программу из БД
    queried_program = db.query(Program).filter(Program.name == "Test Program").first()
    
    assert queried_program is not None
    assert queried_program.name == "Test Program"
    assert queried_program.duration == 60
    assert queried_program.type == ProgramType.MUSIC
    assert queried_program.playlist_id == playlist.id
    assert queried_program.user_id == user.id


def test_program_schedule_model(db):
    """Тест создания расписания программы"""
    from datetime import datetime, timedelta
    
    # Создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    
    # Создаем программу
    program = Program(
        name="Test Program",
        description="Test Program Description",
        duration=60,
        type=ProgramType.MUSIC,
        user_id=user.id
    )
    db.add(program)
    db.commit()
    
    # Настраиваем время начала и окончания
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=60)
    
    # Создаем расписание программы
    schedule = ProgramSchedule(
        program_id=program.id,
        start_time=start_time,
        end_time=end_time,
        repeat_type=RepeatType.ONCE,
        priority=1
    )
    db.add(schedule)
    db.commit()
    
    # Получаем расписание из БД
    queried_schedule = db.query(ProgramSchedule).filter(
        ProgramSchedule.program_id == program.id
    ).first()
    
    assert queried_schedule is not None
    assert queried_schedule.program_id == program.id
    assert queried_schedule.repeat_type == RepeatType.ONCE
    assert queried_schedule.priority == 1 