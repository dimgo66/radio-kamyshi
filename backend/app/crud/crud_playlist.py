from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.playlist import Playlist, PlaylistTrack
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate


class CRUDPlaylist(CRUDBase[Playlist, PlaylistCreate, PlaylistUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: PlaylistCreate, user_id: int
    ) -> Playlist:
        db_obj = Playlist(
            name=obj_in.name,
            description=obj_in.description,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Добавляем треки в плейлист, если они указаны
        if obj_in.track_ids:
            self.update_playlist_tracks(db, db_obj.id, obj_in.track_ids)
            db.refresh(db_obj)
            
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Playlist]:
        return (
            db.query(self.model)
            .filter(Playlist.user_id == user_id)
            .order_by(desc(Playlist.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_playlist_tracks(self, db: Session, playlist_id: int, track_ids: List[int]) -> None:
        # Удаляем существующие треки
        db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == playlist_id).delete()
        db.commit()
        
        # Добавляем новые треки
        for position, track_id in enumerate(track_ids):
            db_obj = PlaylistTrack(
                playlist_id=playlist_id,
                track_id=track_id,
                position=position
            )
            db.add(db_obj)
        
        db.commit()
    
    def get_playlist_with_tracks(self, db: Session, playlist_id: int) -> Optional[Playlist]:
        return (
            db.query(Playlist)
            .filter(Playlist.id == playlist_id)
            .first()
        )


playlist = CRUDPlaylist(Playlist) 