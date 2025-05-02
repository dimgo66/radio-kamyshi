"""
Тесты для моделей данных (упрощенная версия)
"""
import sqlalchemy as sa
import pytest
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import enum
from datetime import datetime

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

class Program(Base):
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # в минутах
    type = Column(Enum(ProgramType))
    playlist_id = Column(Integer, ForeignKey("playlists.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User")
    playlist = relationship("Playlist")
    schedules = relationship("ProgramSchedule", back_populates="program")

class ProgramSchedule(Base):
    __tablename__ = "program_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    repeat_type = Column(Enum(RepeatType))
    priority = Column(Integer, default=1)
    
    program = relationship("Program", back_populates="schedules")

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
    queried_user = db.query(User).first()
    
    assert queried_user is not None
    assert queried_user.email == "test@example.com"
    assert queried_user.username == "testuser"
    assert queried_user.is_active is True
    assert queried_user.is_superuser is False


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
    queried_track = db.query(Track).first()
    
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
    queried_playlist = db.query(Playlist).first()
    
    assert queried_playlist is not None
    assert queried_playlist.name == "Test Playlist"
    assert queried_playlist.description == "Test Description"
    assert queried_playlist.user_id == user.id

def test_playlist_track_relationship(db):
    """Тест отношений между плейлистом и треками"""
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
    
    # Создаем треки
    track1 = Track(
        title="Track 1",
        artist="Artist 1",
        file_path="/path/to/file1.mp3",
        duration=180.0,
        user_id=user.id
    )
    track2 = Track(
        title="Track 2",
        artist="Artist 2",
        file_path="/path/to/file2.mp3",
        duration=240.0,
        user_id=user.id
    )
    db.add(track1)
    db.add(track2)
    db.commit()
    
    # Создаем связи между плейлистом и треками
    playlist_track1 = PlaylistTrack(
        playlist_id=playlist.id,
        track_id=track1.id,
        position=1
    )
    playlist_track2 = PlaylistTrack(
        playlist_id=playlist.id,
        track_id=track2.id,
        position=2
    )
    
    db.add(playlist_track1)
    db.add(playlist_track2)
    db.commit()
    
    # Проверяем, что связи корректно установлены
    queried_playlist = db.query(Playlist).first()
    assert len(queried_playlist.playlist_tracks) == 2
    
    # Проверяем порядок треков в плейлисте
    tracks = db.query(PlaylistTrack).all()
    
    assert tracks[0].track_id == track1.id
    assert tracks[0].position == 1
    assert tracks[1].track_id == track2.id
    assert tracks[1].position == 2

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
    queried_program = db.query(Program).first()
    
    assert queried_program is not None
    assert queried_program.name == "Test Program"
    assert queried_program.duration == 60
    assert queried_program.type == ProgramType.MUSIC
    assert queried_program.playlist_id == playlist.id
    assert queried_program.user_id == user.id

def test_program_schedule(db):
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
    
    # Создаем время начала и окончания
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    
    # Создаем расписание
    schedule = ProgramSchedule(
        program_id=program.id,
        start_time=start_time,
        end_time=end_time,
        repeat_type=RepeatType.WEEKLY,
        priority=2
    )
    db.add(schedule)
    db.commit()
    
    # Проверяем, что расписание создано правильно
    queried_schedule = db.query(ProgramSchedule).first()
    
    assert queried_schedule is not None
    assert queried_schedule.program_id == program.id
    assert queried_schedule.repeat_type == RepeatType.WEEKLY
    assert queried_schedule.priority == 2
    
    # Проверяем связь с программой
    assert queried_schedule.program.name == "Test Program"

def test_complex_relationships(db):
    """Тест комплексных отношений между моделями"""
    from datetime import datetime, timedelta
    
    # Создаем пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    db.commit()  # Коммитим, чтобы получить id пользователя
    
    # Создаем несколько треков
    tracks = []
    for i in range(5):
        track = Track(
            title=f"Track {i+1}",
            artist=f"Artist {i+1}",
            file_path=f"/path/to/file{i+1}.mp3",
            duration=180 + i*30,
            user_id=user.id
        )
        db.add(track)
        tracks.append(track)
    db.commit()  # Коммитим, чтобы получить id треков
    
    # Создаем плейлист
    playlist = Playlist(
        name="Music Playlist",
        description="Playlist for music program",
        user_id=user.id
    )
    db.add(playlist)
    db.commit()  # Коммитим, чтобы получить id плейлиста
    
    # Добавляем треки в плейлист
    for i, track in enumerate(tracks):
        playlist_track = PlaylistTrack(
            playlist_id=playlist.id,
            track_id=track.id,
            position=i+1
        )
        db.add(playlist_track)
    db.commit()  # Коммитим связи плейлист-трек
    
    # Создаем программу на основе плейлиста
    program = Program(
        name="Music Hour",
        description="Hourly music program",
        duration=60,
        type=ProgramType.MUSIC,
        playlist_id=playlist.id,
        user_id=user.id
    )
    db.add(program)
    db.commit()  # Коммитим, чтобы получить id программы
    
    # Проверяем, что программа создана и сохранена
    assert program.id is not None, "Программа не была сохранена в БД"
    
    # Создаем расписание для программы
    now = datetime.now()
    
    # Ежедневное расписание на неделю вперед
    for i in range(7):
        start = now + timedelta(days=i, hours=12)  # Каждый день в 12:00
        end = start + timedelta(hours=1)
        
        schedule = ProgramSchedule(
            program_id=program.id,
            start_time=start,
            end_time=end,
            repeat_type=RepeatType.DAILY,
            priority=1
        )
        db.add(schedule)
    
    # Обязательно коммитим после добавления расписаний
    db.commit()
    
    # Выводим отладочную информацию
    schedules = db.query(ProgramSchedule).all()
    print(f"Создано {len(schedules)} расписаний для программы с ID {program.id}")
    for s in schedules:
        print(f"  Расписание ID: {s.id}, Программа ID: {s.program_id}, Тип повтора: {s.repeat_type}")
    
    # Проверки
    # 1. Плейлист содержит все треки
    assert db.query(PlaylistTrack).count() == 5
    
    # 2. Программа связана с плейлистом
    queried_program = db.query(Program).first()
    assert queried_program.playlist_id == playlist.id
    
    # 3. Для программы создано 7 расписаний
    schedule_count = db.query(ProgramSchedule).count()
    assert schedule_count == 7, f"Ожидалось 7 расписаний, но найдено {schedule_count}"
    
    # 4. Пользователь имеет доступ ко всем созданным объектам
    track_count = db.query(Track).count()
    assert track_count == 5
    
    playlist_count = db.query(Playlist).count()
    assert playlist_count == 1
    
    program_count = db.query(Program).count()
    assert program_count == 1 