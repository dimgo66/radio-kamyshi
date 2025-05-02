"""
Упрощенный тестовый скрипт для проверки имен таблиц без подключения к базе данных
"""
from app.models.user import User
from app.models.track import Track
from app.models.playlist import Playlist, PlaylistTrack
from app.models.program import Program, ProgramSchedule


def main():
    """
    Проверка, что модели имеют ожидаемые имена таблиц
    """
    models = [
        (User, "user"),
        (Track, "track"),
        (Playlist, "playlist"),
        (PlaylistTrack, "playlist_track"),
        (Program, "programs"),
        (ProgramSchedule, "program_schedules"),
    ]
    
    for model_class, expected_table_name in models:
        actual_name = model_class.__tablename__
        print(f"Модель {model_class.__name__}:")
        print(f"  Ожидаемое имя таблицы: {expected_table_name}")
        print(f"  Фактическое имя таблицы: {actual_name}")
        print(f"  Совпадение: {'✓' if actual_name == expected_table_name else '✗'}")
        print()


if __name__ == "__main__":
    main() 