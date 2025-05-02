from typing import Any, Dict
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

# Создаем базовый класс для моделей
Base = declarative_base()

class BaseModel:
    """
    Базовый класс с дополнительной функциональностью для моделей.
    Используется как миксин для наследования вместе с Base.
    
    Пример:
        class User(Base, BaseModel):
            __tablename__ = "users"
            # ...определение полей...
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует модель в словарь.
        """
        return {column.name: getattr(self, column.name) 
                for column in self.__table__.columns} 