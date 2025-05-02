import requests
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_icecast_stats() -> Dict:
    """
    Получает статистику от Icecast-сервера и возвращает информацию о текущем статусе вещания.
    """
    try:
        url = f"{settings.ICECAST_URL}/status-json.xsl"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return {
            "server_status": "online",
            "server_start": data.get("server_start", ""),
            "admin": data.get("admin", ""),
            "host": data.get("host", ""),
            "location": data.get("location", ""),
            "server_id": data.get("server_id", ""),
            "sources": parse_sources(data.get("icestats", {}).get("source", [])),
            "clients": data.get("icestats", {}).get("clients", 0),
            "listeners": data.get("icestats", {}).get("listeners", 0),
            "connections": data.get("icestats", {}).get("connections", 0),
        }
    except Exception as e:
        logger.error(f"Error getting Icecast stats: {e}")
        return {
            "server_status": "offline",
            "error": str(e),
            "sources": [],
            "clients": 0,
            "listeners": 0,
            "connections": 0,
        }

def parse_sources(sources_data) -> List[Dict]:
    """
    Обрабатывает информацию об источниках Icecast.
    """
    if not sources_data:
        return []
    
    # Убеждаемся, что работаем со списком
    if isinstance(sources_data, dict):
        sources_data = [sources_data]
    
    sources = []
    for source in sources_data:
        mount = source.get("mount", "")
        if not mount:
            continue
            
        sources.append({
            "mount": mount,
            "listeners": source.get("listeners", 0),
            "connected": source.get("connected", 0),
            "title": source.get("title", ""),
            "artist": source.get("artist", ""),
            "genre": source.get("genre", ""),
            "bitrate": source.get("bitrate", 0),
            "is_active": True
        })
    
    return sources

def update_metadata(mount: str, title: str, artist: Optional[str] = None) -> bool:
    """
    Обновляет метаданные трека на Icecast-сервере.
    """
    try:
        # Базовый URL для обновления метаданных
        url = f"{settings.ICECAST_URL}/admin/metadata"
        
        # Подготавливаем данные
        data = {
            "mount": mount,
            "mode": "updinfo",
            "song": f"{artist} - {title}" if artist else title
        }
        
        # Добавляем авторизацию, если она настроена
        auth = None
        if settings.ICECAST_ADMIN_USER and settings.ICECAST_ADMIN_PASSWORD:
            auth = (settings.ICECAST_ADMIN_USER, settings.ICECAST_ADMIN_PASSWORD)
        
        # Отправляем запрос
        response = requests.get(url, params=data, auth=auth, timeout=5)
        response.raise_for_status()
        
        logger.info(f"Updated metadata for {mount}: {data['song']}")
        return True
    except Exception as e:
        logger.error(f"Error updating Icecast metadata: {e}")
        return False

def get_stream_status(mount: str) -> Dict:
    """
    Получает статус конкретного потока по его mount point.
    """
    stats = get_icecast_stats()
    
    for source in stats.get("sources", []):
        if source.get("mount") == mount:
            return {
                "status": "online",
                "listeners": source.get("listeners", 0),
                "title": source.get("title", ""),
                "artist": source.get("artist", ""),
                "bitrate": source.get("bitrate", 0),
            }
    
    return {
        "status": "offline",
        "listeners": 0,
        "title": "",
        "artist": "",
        "bitrate": 0,
    } 