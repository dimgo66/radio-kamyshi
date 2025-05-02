"""
Тестовый скрипт для проверки моделей данных
"""
from sqlalchemy import inspect

from app.db.session import engine
from app.models.user import User
from app.models.track import Track
from app.models.playlist import Playlist, PlaylistTrack
from app.models.program import Program, ProgramSchedule


def main():
    """
    Проверка, что модели правильно определены и имеют правильные имена таблиц
    """
    inspector = inspect(engine)
    
    for cls in [User, Track, Playlist, PlaylistTrack, Program, ProgramSchedule]:
        print(f"Проверка модели {cls.__name__}:")
        print(f"  Имя таблицы: {cls.__tablename__}")
        print(f"  Ожидаемые колонки: {[c.name for c in cls.__table__.columns]}")
        print()


if __name__ == "__main__":
    main() 