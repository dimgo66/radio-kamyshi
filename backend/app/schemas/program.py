from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.program import ProgramStatus
from app.schemas.playlist import Playlist


# Общие свойства
class ProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int = Field(..., description="Длительность в минутах")
    type: str
    playlist_id: Optional[int] = None
    image_url: Optional[str] = None
    is_active: bool = True


# Создание программы
class ProgramCreate(ProgramBase):
    pass


# Обновление программы
class ProgramUpdate(ProgramBase):
    name: Optional[str] = None
    duration: Optional[int] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None


# Полная информация о программе
class ProgramInDBBase(ProgramBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Расширенная информация о программе
class Program(ProgramInDBBase):
    status: Optional[ProgramStatus] = None
    user_id: int
    playlist_id: int
    
    class Config:
        from_attributes = True


# Расширенная информация о программе
class ProgramDetail(Program):
    playlist: Playlist
    
    class Config:
        from_attributes = True


class ProgramScheduleBase(BaseModel):
    program_id: int
    start_time: datetime
    end_time: datetime
    repeat_type: str
    repeat_days: Optional[List[int]] = None
    priority: int = 1
    is_active: bool = True


class ProgramScheduleCreate(ProgramScheduleBase):
    pass


class ProgramScheduleUpdate(ProgramScheduleBase):
    program_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    repeat_type: Optional[str] = None
    repeat_days: Optional[List[int]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class ProgramScheduleInDBBase(ProgramScheduleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProgramScheduleInDB(ProgramScheduleInDBBase):
    pass


class ProgramInDB(ProgramInDBBase):
    schedules: List[ProgramScheduleInDB] = [] 