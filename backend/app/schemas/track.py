from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Общие свойства
class TrackBase(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None


# Свойства для создания трека
class TrackCreate(TrackBase):
    title: str
    file_path: str
    duration: float


# Свойства для обновления трека
class TrackUpdate(TrackBase):
    is_active: Optional[bool] = None


# Свойства, возвращаемые клиенту
class Track(TrackBase):
    id: int
    file_path: str
    file_size: Optional[int] = None
    duration: float
    format: Optional[str] = None
    bitrate: Optional[int] = None
    waveform_data: Optional[str] = None
    
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    
    class Config:
        from_attributes = True


# Расширенная информация о треке
class TrackDetail(Track):
    pass 