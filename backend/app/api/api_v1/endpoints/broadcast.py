from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.tasks.broadcaster.icecast_tasks import get_icecast_stats, get_stream_status, update_metadata
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/status", response_model=Dict)
def get_broadcast_status():
    """
    Получает текущий статус вещания.
    """
    return get_icecast_stats()

@router.get("/stream/{mount}", response_model=Dict)
def get_specific_stream_status(mount: str):
    """
    Получает статус конкретного потока.
    """
    return get_stream_status(mount)

@router.post("/metadata/{mount}", response_model=Dict)
def update_stream_metadata(
    mount: str,
    title: str,
    artist: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновляет метаданные трека на потоке.
    Требует аутентификацию.
    """
    success = update_metadata(mount, title, artist)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить метаданные."
        )
    
    return {
        "success": True,
        "message": "Метаданные успешно обновлены",
        "mount": mount,
        "title": title,
        "artist": artist
    } 