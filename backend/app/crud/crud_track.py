from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.track import Track
from app.schemas.track import TrackCreate, TrackUpdate


class CRUDTrack(CRUDBase[Track, TrackCreate, TrackUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: TrackCreate, user_id: int
    ) -> Track:
        db_obj = Track(
            title=obj_in.title,
            artist=obj_in.artist,
            album=obj_in.album,
            genre=obj_in.genre,
            year=obj_in.year,
            file_path=obj_in.file_path,
            duration=obj_in.duration,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Track]:
        return (
            db.query(self.model)
            .filter(Track.user_id == user_id)
            .order_by(desc(Track.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_tracks(
        self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Track]:
        search = f"%{search_term}%"
        return (
            db.query(self.model)
            .filter(
                (Track.title.ilike(search)) |
                (Track.artist.ilike(search)) |
                (Track.album.ilike(search)) |
                (Track.genre.ilike(search))
            )
            .order_by(desc(Track.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )


track = CRUDTrack(Track) 