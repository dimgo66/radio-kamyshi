"""
Тестовый скрипт для проверки всех моделей в проекте
"""
from app.models.user import User
from app.models.track import Track
from app.models.playlist import Playlist, PlaylistTrack
from app.models.program import Program, ProgramSchedule


def main():
    """
    Проверка всех моделей в проекте
    """
    models = [
        User,
        Track,
        Playlist,
        PlaylistTrack,
        Program,
        ProgramSchedule
    ]
    
    for model in models:
        print(f"Модель {model.__name__}:")
        print(f"  Имя таблицы: {model.__tablename__}")
        print(f"  Колонки: {[c.name for c in model.__table__.columns if hasattr(model.__table__, 'columns')]}")
        print(f"  Отношения: {[r for r in dir(model) if not r.startswith('_') and not r in [c.name for c in model.__table__.columns if hasattr(model.__table__, 'columns')]]}")
        print()


if __name__ == "__main__":
    main() 