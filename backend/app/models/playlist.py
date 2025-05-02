from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Playlist(Base):
    __tablename__ = "playlist"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Внешние ключи
    user_id = Column(Integer, ForeignKey("user.id"))
    
    # Отношения
    user = relationship("User", back_populates="playlists")
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")
    programs = relationship("Program", back_populates="playlist")


class PlaylistTrack(Base):
    __tablename__ = "playlist_track"
    
    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer, nullable=False)  # Порядок трека в плейлисте
    
    # Внешние ключи
    playlist_id = Column(Integer, ForeignKey("playlist.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("track.id"), nullable=False)
    
    # Отношения
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track", back_populates="playlist_tracks") 