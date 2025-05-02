import os
import shutil
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_db, get_current_active_user
from app.core.config import settings
from app.tasks.track_processing import process_audio_file

router = APIRouter()


@router.get("/", response_model=List[schemas.Track])
def read_tracks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    search: Optional[str] = Query(None),
) -> Any:
    """
    Получить список треков текущего пользователя.
    Опционально: поиск по имени или исполнителю.
    """
    if search:
        tracks = crud.track.search_tracks(db, search_term=search, skip=skip, limit=limit)
    else:
        tracks = crud.track.get_multi_by_owner(
            db=db, user_id=current_user.id, skip=skip, limit=limit
        )
    return tracks


@router.post("/", response_model=schemas.Track)
def create_track(
    *,
    db: Session = Depends(get_db),
    title: str = Form(...),
    artist: Optional[str] = Form(None),
    album: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    audio_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Загрузить новый трек.
    """
    # Создаем директорию для хранения файлов пользователя, если она не существует
    user_media_dir = os.path.join(settings.MEDIA_DIR, str(current_user.id))
    os.makedirs(user_media_dir, exist_ok=True)
    
    # Путь для сохранения файла
    file_path = os.path.join(user_media_dir, audio_file.filename)
    
    # Проверка на уникальность файла
    # Если такой файл существует, добавляем к имени префикс
    if os.path.exists(file_path):
        base_name, ext = os.path.splitext(audio_file.filename)
        count = 1
        while os.path.exists(file_path):
            file_path = os.path.join(user_media_dir, f"{base_name}_{count}{ext}")
            count += 1
    
    try:
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Создаем запись в БД (длительность временно 0, обновится после обработки)
        track_in = schemas.TrackCreate(
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            year=year,
            file_path=file_path,
            duration=0  # Временное значение
        )
        
        track = crud.track.create_with_owner(
            db=db, obj_in=track_in, user_id=current_user.id
        )
        
        # Запускаем асинхронную обработку аудиофайла
        process_audio_file.delay(track.id)
        
        return track
    
    except Exception as e:
        # Если произошла ошибка, удаляем файл, если он был создан
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.get("/{track_id}", response_model=schemas.Track)
def read_track(
    *,
    db: Session = Depends(get_db),
    track_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить информацию о треке по ID.
    """
    track = crud.track.get(db=db, id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к этому треку")
    return track


@router.get("/{track_id}/download")
def download_track(
    *,
    db: Session = Depends(get_db),
    track_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Скачать аудиофайл.
    """
    track = crud.track.get(db=db, id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к этому треку")
    
    if not os.path.exists(track.file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        track.file_path,
        media_type="audio/mpeg",
        filename=os.path.basename(track.file_path)
    )


@router.put("/{track_id}", response_model=schemas.Track)
def update_track(
    *,
    db: Session = Depends(get_db),
    track_id: int,
    track_in: schemas.TrackUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить информацию о треке.
    """
    track = crud.track.get(db=db, id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к этому треку")
    
    track = crud.track.update(db=db, db_obj=track, obj_in=track_in)
    return track


@router.delete("/{track_id}", response_model=schemas.Track)
def delete_track(
    *,
    db: Session = Depends(get_db),
    track_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить трек.
    """
    track = crud.track.get(db=db, id=track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Трек не найден")
    if track.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для доступа к этому треку")
    
    # Удаляем файл с диска, если он существует
    if os.path.exists(track.file_path):
        os.remove(track.file_path)
    
    track = crud.track.remove(db=db, id=track_id)
    return track 