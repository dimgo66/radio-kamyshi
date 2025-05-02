"""
Модуль для обработки аудио файлов
"""
import os
import subprocess
import json
import tempfile
import re
from typing import Dict, Any, List, Optional, Union

try:
    import mutagen
    from mutagen._file import File as MutagenFile
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.wave import WAVE
except ImportError:
    print("Warning: mutagen is not installed. Audio metadata extraction will not work.")


class AudioProcessor:
    """
    Класс для обработки аудио файлов
    """
    
    def __init__(self, storage_dir: str = "/tmp"):
        """
        Инициализация процессора аудио
        
        Args:
            storage_dir: Директория для хранения аудио файлов
        """
        self.storage_dir = storage_dir
        self.allowed_extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Извлечение метаданных из аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            
        Returns:
            Словарь с метаданными
        """
        try:
            audio = MutagenFile(file_path)
            metadata = {
                "title": "Unknown",
                "artist": "Unknown",
                "album": "Unknown",
                "genre": "Unknown",
                "duration": 0.0,
                "file_size": os.path.getsize(file_path),
                "file_name": os.path.basename(file_path)
            }
            
            if audio is not None:
                # Получаем длительность
                if hasattr(audio, "info") and hasattr(audio.info, "length"):
                    metadata["duration"] = audio.info.length
                
                # Получаем метаданные из тегов
                if hasattr(audio, "tags") and audio.tags:
                    # Обрабатываем теги
                    tags_to_check = ["title", "artist", "album", "genre"]
                    for tag in tags_to_check:
                        if tag in audio.tags:
                            value = audio.tags[tag]
                            if isinstance(value, list) and value:
                                metadata[tag] = value[0]
                            else:
                                metadata[tag] = value
            
            return metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                "title": "Unknown",
                "artist": "Unknown",
                "album": "Unknown",
                "genre": "Unknown",
                "duration": 0.0,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "file_name": os.path.basename(file_path),
                "error": str(e)
            }
    
    def format_duration(self, seconds: float) -> str:
        """
        Форматирование длительности в секундах в формат HH:MM:SS
        
        Args:
            seconds: Длительность в секундах
            
        Returns:
            Отформатированная строка времени
        """
        if seconds < 0:
            seconds = 0
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02}:{secs:02}"
        else:
            return f"{minutes:02}:{secs:02}"
    
    def validate_audio_file(self, file_path: str, max_size_mb: int = 100) -> bool:
        """
        Проверка аудио файла на корректность
        
        Args:
            file_path: Путь к аудио файлу
            max_size_mb: Максимальный размер файла в МБ
            
        Returns:
            True если файл корректный, иначе False
        """
        # Проверяем расширение
        file_ext = os.path.splitext(os.path.basename(file_path))[1].lower()
        if file_ext not in self.allowed_extensions:
            return False
        
        # Проверяем размер файла
        file_size = os.path.getsize(file_path)
        if file_size > max_size_mb * 1024 * 1024:
            return False
        
        return True
    
    def convert_to_mp3(self, file_path: str, bitrate: int = 320) -> str:
        """
        Конвертация аудио файла в MP3
        
        Args:
            file_path: Путь к аудио файлу
            bitrate: Битрейт для MP3 (кбит/с)
            
        Returns:
            Путь к сконвертированному MP3 файлу
        """
        # Создаем выходной путь
        filename = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(self.storage_dir, f"{filename}.mp3")
        
        # Запускаем ffmpeg для конвертации
        cmd = [
            "ffmpeg", "-i", file_path, 
            "-codec:a", "libmp3lame", 
            "-b:a", f"{bitrate}k",
            "-y",  # Перезаписывать существующий файл
            output_path
        ]
        
        try:
            # Выполняем команду
            result = subprocess.run(cmd, check=True, capture_output=True)
            if result.returncode == 0:
                return output_path
            else:
                print(f"Error converting audio: {result.stderr.decode()}")
                return file_path
        except Exception as e:
            print(f"Error converting audio: {e}")
            return file_path
    
    def generate_waveform(self, file_path: str, pixels_per_second: int = 10) -> Dict[str, Any]:
        """
        Генерация данных о форме волны аудио файла
        
        Args:
            file_path: Путь к аудио файлу
            pixels_per_second: Количество точек на секунду
            
        Returns:
            Словарь с данными формы волны
        """
        # Создаем временный файл для JSON
        json_output = os.path.join(tempfile.gettempdir(), f"{os.path.basename(file_path)}.json")
        
        # Запускаем audiowaveform для генерации данных
        cmd = [
            "audiowaveform",
            "-i", file_path,
            "-o", json_output,
            "-b", "8",  # 8 бит на сэмпл
            "--pixels-per-second", str(pixels_per_second),
            "-q"  # Тихий режим
        ]
        
        try:
            # Выполняем команду
            result = subprocess.run(cmd, check=True, capture_output=True)
            if result.returncode == 0 and os.path.exists(json_output):
                # Читаем сгенерированные данные
                with open(json_output, 'r') as f:
                    waveform_data = json.load(f)
                
                # Удаляем временный файл
                os.unlink(json_output)
                
                return waveform_data
            else:
                return {
                    "data": [],
                    "sample_rate": 0,
                    "channels": 0,
                    "duration": 0
                }
        except Exception as e:
            print(f"Error generating waveform: {e}")
            return {
                "data": [],
                "sample_rate": 0,
                "channels": 0,
                "duration": 0,
                "error": str(e)
            }


def calculate_duration_ms(time_str: Optional[str]) -> int:
    """
    Расчет длительности в миллисекундах из строки времени формата HH:MM:SS или MM:SS
    
    Args:
        time_str: Строка времени
        
    Returns:
        Длительность в миллисекундах
    """
    if not time_str:
        return 0
    
    try:
        # Определяем формат времени
        parts = time_str.split(":")
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return (hours * 3600 + minutes * 60 + seconds) * 1000
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return (minutes * 60 + seconds) * 1000
        else:
            return 0
    except (ValueError, AttributeError):
        return 0


def format_duration_from_ms(ms: int) -> str:
    """
    Форматирование длительности из миллисекунд в формат HH:MM:SS или MM:SS
    
    Args:
        ms: Длительность в миллисекундах
        
    Returns:
        Отформатированная строка времени
    """
    if ms < 0:
        ms = 0
    
    # Преобразуем миллисекунды в секунды
    total_seconds = ms // 1000
    
    # Разбиваем на часы, минуты и секунды
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # Форматируем
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes:02}:{seconds:02}"


def parse_time_to_seconds(time_str: Optional[str]) -> int:
    """
    Преобразование строки времени в секунды
    
    Args:
        time_str: Строка времени формата HH:MM:SS или MM:SS
        
    Returns:
        Время в секундах
    """
    return calculate_duration_ms(time_str) // 1000 