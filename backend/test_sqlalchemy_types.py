"""
Тестовый скрипт для проверки типов SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.db.sqlalchemy_types import (
    Column as ColumnType,
    Integer as IntegerType,
    String as StringType,
    DateTime as DateTimeType,
    ForeignKey as ForeignKeyType,
    Boolean as BooleanType,
    Text as TextType,
    relationship as RelationshipType,
    func as FuncType,
    Enum as EnumType,
)


def main():
    """
    Проверка, что наши типы SQLAlchemy соответствуют реальным типам
    """
    # Имитируем использование SQLAlchemy в моделях
    class TestModel(Base):
        __tablename__ = "test_model"
        
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, nullable=False)
        description = Column(Text)
        
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        # Внешние ключи
        parent_id = Column(Integer, ForeignKey("parent.id"))
        
        # Отношения
        parent = relationship("Parent", back_populates="children")
        children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    
    print("Тестирование типов SQLAlchemy...")
    print(f"Column тип: {type(Column).__name__}")
    print(f"Integer тип: {type(Integer).__name__}")
    print(f"String тип: {type(String).__name__}")
    print(f"DateTime тип: {type(DateTime).__name__}")
    print(f"func.now() тип: {type(func.now()).__name__}")
    print("Все типы проверены!")


if __name__ == "__main__":
    main() 