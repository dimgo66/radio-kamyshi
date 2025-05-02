import logging
import requests
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

class SubapseClient:
    def __init__(self):
        self.base_url = f"http://{settings.SUBAPSE_HOST}:{settings.SUBAPSE_PORT}"
        self.timeout = 10

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Выполняет HTTP запрос к Subapse API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Subapse API error: {str(e)}")
            raise

    def start_broadcast(
        self,
        playlist_path: str,
        mount_point: str,
        icecast_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Запускает трансляцию через Subapse."""
        data = {
            "playlist": playlist_path,
            "icecast": {
                **icecast_config,
                "mount": mount_point
            }
        }
        return self._make_request("POST", "/start", data)

    def stop_broadcast(self, mount_point: str) -> Dict[str, Any]:
        """Останавливает трансляцию."""
        data = {
            "mount": mount_point
        }
        return self._make_request("POST", "/stop", data)

    def get_status(self, mount_point: Optional[str] = None) -> Dict[str, Any]:
        """Получает статус трансляции."""
        endpoint = f"/status{f'/{mount_point}' if mount_point else ''}"
        return self._make_request("GET", endpoint)

# Создаем глобальный экземпляр клиента
subapse = SubapseClient() 