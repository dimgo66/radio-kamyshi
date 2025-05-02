"""
Скрипт для проверки импортов в проекте Radio Kamyshi
"""

try:
    import fastapi
    import fastapi.security
    import sqlalchemy
    import sqlalchemy.orm
    import sqlalchemy.sql
    import pydantic
    print("Все необходимые библиотеки успешно импортированы!")
except ImportError as e:
    print(f"Ошибка импорта: {e}") 