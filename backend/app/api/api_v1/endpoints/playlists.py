from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_db, get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[schemas.Playlist])
def read_playlists(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить список плейлистов текущего пользователя.
    """
    playlists = crud.playlist.get_multi_by_owner(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return playlists


@router.post("/", response_model=schemas.Playlist)
def create_playlist(
    *,
    db: Session = Depends(get_db),
    playlist_in: schemas.PlaylistCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Создать новый плейлист.
    """
    playlist = crud.playlist.create_with_owner(db=db, obj_in=playlist_in, user_id=current_user.id)
    return playlist


@router.get("/{playlist_id}", response_model=schemas.Playlist)
def read_playlist(
    *,
    db: Session = Depends(get_db),
    playlist_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить плейлист по ID.
    """
    playlist = crud.playlist.get(db=db, id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Плейлист не найден")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для доступа к этому плейлисту"
        )
    return playlist


@router.put("/{playlist_id}", response_model=schemas.Playlist)
def update_playlist(
    *,
    db: Session = Depends(get_db),
    playlist_id: int,
    playlist_in: schemas.PlaylistUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить плейлист.
    """
    playlist = crud.playlist.get(db=db, id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Плейлист не найден")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для изменения этого плейлиста"
        )
    
    # Обновляем плейлист
    playlist = crud.playlist.update(db=db, db_obj=playlist, obj_in=playlist_in)
    
    # Если в запросе были переданы треки, обновляем их
    if playlist_in.track_ids is not None:
        crud.playlist.update_playlist_tracks(db, playlist_id, playlist_in.track_ids)
    
    return crud.playlist.get_playlist_with_tracks(db, playlist_id)


@router.delete("/{playlist_id}", response_model=schemas.Playlist)
def delete_playlist(
    *,
    db: Session = Depends(get_db),
    playlist_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить плейлист.
    """
    playlist = crud.playlist.get(db=db, id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Плейлист не найден")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для удаления этого плейлиста"
        )
    
    playlist = crud.playlist.remove(db=db, id=playlist_id)
    return playlist 