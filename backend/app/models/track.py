from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Track(Base):
    __tablename__ = "track"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    artist = Column(String, index=True)
    album = Column(String)
    genre = Column(String)
    year = Column(Integer)
    
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # Размер в байтах
    duration = Column(Float, nullable=False)  # Длительность в секундах
    format = Column(String)  # mp3, wav, flac и т.д.
    bitrate = Column(Integer)  # в kb/s
    
    waveform_data = Column(Text)  # JSON строка с данными визуализации
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Внешние ключи
    user_id = Column(Integer, ForeignKey("user.id"))
    
    # Отношения
    user = relationship("User", back_populates="tracks")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track") 