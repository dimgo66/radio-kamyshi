import os
import json
import logging
import tempfile
import subprocess
from typing import Dict, Any, Optional
import shutil
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE

from app.core.celery import celery_app
from app.core.config import settings
from app.crud import track as track_crud
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def get_audio_metadata(file_path: str) -> Dict[str, Any]:
    """Извлекает метаданные из аудиофайла."""
    try:
        audio = None
        format_name = ""
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".mp3":
            audio = MP3(file_path)
            format_name = "mp3"
        elif ext == ".flac":
            audio = FLAC(file_path)
            format_name = "flac"
        elif ext == ".wav":
            audio = WAVE(file_path)
            format_name = "wav"
        else:
            audio = mutagen.File(file_path)
            format_name = ext[1:]  # Удаляем точку
            
        metadata = {
            "duration": audio.info.length,
            "format": format_name,
            "bitrate": getattr(audio.info, "bitrate", 0) // 1000 if hasattr(audio.info, "bitrate") else 0,
        }
        
        # Пытаемся извлечь информацию о треке
        if hasattr(audio, "tags") and audio.tags:
            tags = audio.tags
            
            if isinstance(tags, dict):
                metadata["title"] = tags.get("title", [""])[0] if isinstance(tags.get("title", [""]), list) else tags.get("title", "")
                metadata["artist"] = tags.get("artist", [""])[0] if isinstance(tags.get("artist", [""]), list) else tags.get("artist", "")
                metadata["album"] = tags.get("album", [""])[0] if isinstance(tags.get("album", [""]), list) else tags.get("album", "")
                metadata["genre"] = tags.get("genre", [""])[0] if isinstance(tags.get("genre", [""]), list) else tags.get("genre", "")
                metadata["year"] = tags.get("date", [""])[0] if isinstance(tags.get("date", [""]), list) else tags.get("date", "")
            else:
                # Если это ID3 теги в MP3
                metadata["title"] = str(getattr(tags, "TIT2", "")) if hasattr(tags, "TIT2") else ""
                metadata["artist"] = str(getattr(tags, "TPE1", "")) if hasattr(tags, "TPE1") else ""
                metadata["album"] = str(getattr(tags, "TALB", "")) if hasattr(tags, "TALB") else ""
                metadata["genre"] = str(getattr(tags, "TCON", "")) if hasattr(tags, "TCON") else ""
                metadata["year"] = str(getattr(tags, "TDRC", "")) if hasattr(tags, "TDRC") else ""
                
        # Преобразуем год в число, если возможно
        if "year" in metadata and metadata["year"]:
            try:
                metadata["year"] = int(metadata["year"].split("-")[0])
            except (ValueError, IndexError):
                metadata["year"] = None
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        return {
            "duration": 0,
            "format": "",
            "bitrate": 0,
            "title": "",
            "artist": "",
            "album": "",
            "genre": "",
            "year": None
        }


def generate_waveform(file_path: str, num_points: int = 100) -> str:
    """Генерирует данные для визуализации волны аудио."""
    try:
        # Временный файл для данных waveform
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            # Используем ffmpeg для генерации waveform данных
            # Этот код примерный, в реальности нужно настроить под конкретные нужды
            cmd = [
                "ffmpeg",
                "-i", file_path,
                "-af", f"aresample=8000,asetnsamples={num_points}", 
                "-f", "data", "-y", temp_file.name
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Чтение данных waveform
                with open(temp_file.name, "rb") as f:
                    raw_data = f.read()
                
                # Преобразование байтов в числа
                waveform = []
                for i in range(0, len(raw_data), 2):
                    if i + 1 < len(raw_data):
                        value = int.from_bytes(raw_data[i:i+2], byteorder="little", signed=True)
                        # Нормализация значений от -1 до 1
                        normalized = value / 32768
                        waveform.append(normalized)
                
                # Если количество точек меньше нужного, дополняем
                while len(waveform) < num_points:
                    waveform.append(0)
                
                # Если больше - обрезаем
                waveform = waveform[:num_points]
                
                return json.dumps(waveform)
            
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
                return json.dumps([0] * num_points)
    
    except Exception as e:
        logger.error(f"Error generating waveform: {e}")
        return json.dumps([0] * num_points)


@celery_app.task
def process_audio_file(track_id: int):
    """Обрабатывает загруженный аудиофайл: извлекает метаданные и генерирует waveform."""
    db = SessionLocal()
    
    try:
        track_obj = track_crud.get(db, track_id)
        if not track_obj:
            logger.error(f"Track with ID {track_id} not found")
            return
        
        # Полный путь к файлу
        file_path = track_obj.file_path
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return
        
        # Получаем метаданные
        metadata = get_audio_metadata(file_path)
        
        # Обновляем информацию о треке, если метаданные успешно извлечены
        update_data = {}
        
        # Обновляем поля, только если они не были установлены вручную
        if metadata["duration"] > 0:
            update_data["duration"] = metadata["duration"]
        
        if metadata["format"]:
            update_data["format"] = metadata["format"]
        
        if metadata["bitrate"] > 0:
            update_data["bitrate"] = metadata["bitrate"]
        
        if not track_obj.title and metadata["title"]:
            update_data["title"] = metadata["title"]
        
        if not track_obj.artist and metadata["artist"]:
            update_data["artist"] = metadata["artist"]
        
        if not track_obj.album and metadata["album"]:
            update_data["album"] = metadata["album"]
        
        if not track_obj.genre and metadata["genre"]:
            update_data["genre"] = metadata["genre"]
        
        if not track_obj.year and metadata["year"]:
            update_data["year"] = metadata["year"]
        
        # Получаем размер файла
        update_data["file_size"] = os.path.getsize(file_path)
        
        # Генерируем waveform
        waveform_data = generate_waveform(file_path)
        if waveform_data:
            update_data["waveform_data"] = waveform_data
        
        # Обновляем запись в БД
        track_crud.update(db, db_obj=track_obj, obj_in=update_data)
        
        logger.info(f"Successfully processed audio file for track {track_id}")
    
    except Exception as e:
        logger.error(f"Error processing audio file for track {track_id}: {e}")
    finally:
        db.close() 