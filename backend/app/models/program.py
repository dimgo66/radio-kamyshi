from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class ProgramStatus(str, enum.Enum):
    SCHEDULED = "scheduled"  # Запланировано
    RUNNING = "running"      # Идет вещание
    COMPLETED = "completed"  # Завершено
    CANCELLED = "cancelled"  # Отменено


class ProgramType(str, enum.Enum):
    MUSIC = "music"
    TALK = "talk"
    NEWS = "news"
    SPECIAL = "special"


class RepeatType(str, enum.Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # в минутах
    type = Column(SQLEnum(ProgramType), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlist.id"), nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Внешние ключи
    user_id = Column(Integer, ForeignKey("user.id"))
    
    # Отношения
    user = relationship("User", back_populates="programs")
    playlist = relationship("Playlist", back_populates="programs")
    schedules = relationship("ProgramSchedule", back_populates="program", cascade="all, delete-orphan")


class ProgramSchedule(Base):
    __tablename__ = "program_schedules"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    repeat_type = Column(SQLEnum(RepeatType), nullable=False)
    repeat_days = Column(String, nullable=True)  # JSON строка с массивом дней недели
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    program = relationship("Program", back_populates="schedules") 