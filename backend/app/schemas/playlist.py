from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.track import Track


# Общие свойства
class PlaylistBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Плейлист-трек для манипуляций
class PlaylistTrackBase(BaseModel):
    track_id: int
    position: int


# Создание плейлиста
class PlaylistCreate(PlaylistBase):
    name: str
    track_ids: Optional[List[int]] = None


# Обновление плейлиста
class PlaylistUpdate(PlaylistBase):
    track_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


# Плейлист-трек для API
class PlaylistTrack(PlaylistTrackBase):
    id: int
    track: Track
    
    class Config:
        from_attributes = True


# Полная информация о плейлисте
class Playlist(PlaylistBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: int
    tracks: List[Track] = []
    
    class Config:
        from_attributes = True 