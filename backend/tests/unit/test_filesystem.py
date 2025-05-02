"""
Тесты для проверки работы с файловой системой
"""
import pytest
import os
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Класс для работы с файловой системой
class StorageManager:
    """
    Класс для работы с хранилищем файлов
    """
    
    def __init__(self, base_dir: str):
        """
        Инициализация менеджера хранилища
        
        Args:
            base_dir: Базовая директория для хранения файлов
        """
        self.base_dir = base_dir
        self.ensure_dirs_exist()
    
    def ensure_dirs_exist(self):
        """
        Создает необходимые директории, если они не существуют
        """
        # Директории для разных типов контента
        dirs = [
            "tracks",
            "images",
            "temp",
            "exports"
        ]
        
        for dir_name in dirs:
            dir_path = os.path.join(self.base_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
    
    def get_file_path(self, category: str, filename: str) -> str:
        """
        Получает полный путь к файлу
        
        Args:
            category: Категория файла (tracks, images и т.д.)
            filename: Имя файла
            
        Returns:
            Полный путь к файлу
        """
        return os.path.join(self.base_dir, category, filename)
    
    def save_file(self, category: str, filename: str, content: bytes) -> str:
        """
        Сохраняет файл в хранилище
        
        Args:
            category: Категория файла
            filename: Имя файла
            content: Содержимое файла
            
        Returns:
            Полный путь к сохраненному файлу
        """
        file_path = self.get_file_path(category, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return file_path
    
    def read_file(self, category: str, filename: str) -> bytes:
        """
        Читает файл из хранилища
        
        Args:
            category: Категория файла
            filename: Имя файла
            
        Returns:
            Содержимое файла
            
        Raises:
            FileNotFoundError: Если файл не найден
        """
        file_path = self.get_file_path(category, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        with open(file_path, "rb") as f:
            return f.read()
    
    def delete_file(self, category: str, filename: str) -> bool:
        """
        Удаляет файл из хранилища
        
        Args:
            category: Категория файла
            filename: Имя файла
            
        Returns:
            True, если файл успешно удален, иначе False
        """
        file_path = self.get_file_path(category, filename)
        
        if not os.path.exists(file_path):
            return False
        
        os.remove(file_path)
        return True
    
    def list_files(self, category: str) -> list:
        """
        Возвращает список файлов в указанной категории
        
        Args:
            category: Категория файлов
            
        Returns:
            Список файлов
        """
        dir_path = os.path.join(self.base_dir, category)
        
        if not os.path.exists(dir_path):
            return []
        
        return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    def get_file_info(self, category: str, filename: str) -> dict:
        """
        Получает информацию о файле
        
        Args:
            category: Категория файла
            filename: Имя файла
            
        Returns:
            Словарь с информацией о файле
            
        Raises:
            FileNotFoundError: Если файл не найден
        """
        file_path = self.get_file_path(category, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        stat = os.stat(file_path)
        
        return {
            "name": filename,
            "path": file_path,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": os.path.splitext(filename)[1].lower()
        }

# Фикстуры для тестов
@pytest.fixture
def temp_storage_dir():
    """
    Создает временную директорию для тестов
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def storage_manager(temp_storage_dir):
    """
    Создает экземпляр менеджера хранилища
    """
    return StorageManager(temp_storage_dir)

@pytest.fixture
def test_file_content():
    """
    Возвращает тестовое содержимое файла
    """
    return b"This is a test file content."

# Тесты
def test_ensure_dirs_exist(storage_manager):
    """
    Проверяет создание необходимых директорий
    """
    # Директории уже должны быть созданы при инициализации
    for dir_name in ["tracks", "images", "temp", "exports"]:
        dir_path = os.path.join(storage_manager.base_dir, dir_name)
        assert os.path.exists(dir_path)
        assert os.path.isdir(dir_path)

def test_save_and_read_file(storage_manager, test_file_content):
    """
    Проверяет сохранение и чтение файла
    """
    # Сохраняем файл
    filename = "test_file.txt"
    file_path = storage_manager.save_file("tracks", filename, test_file_content)
    
    # Проверяем, что файл существует
    assert os.path.exists(file_path)
    
    # Читаем файл
    content = storage_manager.read_file("tracks", filename)
    
    # Проверяем содержимое
    assert content == test_file_content

def test_delete_file(storage_manager, test_file_content):
    """
    Проверяет удаление файла
    """
    # Сохраняем файл
    filename = "file_to_delete.txt"
    file_path = storage_manager.save_file("images", filename, test_file_content)
    
    # Проверяем, что файл существует
    assert os.path.exists(file_path)
    
    # Удаляем файл
    result = storage_manager.delete_file("images", filename)
    
    # Проверяем результат
    assert result is True
    assert not os.path.exists(file_path)
    
    # Пробуем удалить несуществующий файл
    result = storage_manager.delete_file("images", "nonexistent.txt")
    assert result is False

def test_list_files(storage_manager, test_file_content):
    """
    Проверяет получение списка файлов
    """
    # Сохраняем несколько файлов
    storage_manager.save_file("tracks", "file1.mp3", test_file_content)
    storage_manager.save_file("tracks", "file2.mp3", test_file_content)
    storage_manager.save_file("tracks", "file3.mp3", test_file_content)
    
    # Получаем список файлов
    files = storage_manager.list_files("tracks")
    
    # Проверяем список
    assert len(files) == 3
    assert "file1.mp3" in files
    assert "file2.mp3" in files
    assert "file3.mp3" in files
    
    # Проверяем пустую директорию
    files = storage_manager.list_files("exports")
    assert len(files) == 0

def test_get_file_info(storage_manager, test_file_content):
    """
    Проверяет получение информации о файле
    """
    # Сохраняем файл
    filename = "info_test.mp3"
    storage_manager.save_file("tracks", filename, test_file_content)
    
    # Получаем информацию о файле
    info = storage_manager.get_file_info("tracks", filename)
    
    # Проверяем информацию
    assert info["name"] == filename
    assert info["size"] == len(test_file_content)
    assert info["extension"] == ".mp3"
    assert "created" in info
    assert "modified" in info
    
    # Проверяем несуществующий файл
    with pytest.raises(FileNotFoundError):
        storage_manager.get_file_info("tracks", "nonexistent.mp3")

def test_file_categories(storage_manager, test_file_content):
    """
    Проверяет работу с разными категориями файлов
    """
    # Сохраняем файлы в разные категории
    storage_manager.save_file("tracks", "track.mp3", test_file_content)
    storage_manager.save_file("images", "image.jpg", test_file_content)
    storage_manager.save_file("temp", "temp.txt", test_file_content)
    
    # Проверяем списки файлов
    assert len(storage_manager.list_files("tracks")) == 1
    assert len(storage_manager.list_files("images")) == 1
    assert len(storage_manager.list_files("temp")) == 1
    assert len(storage_manager.list_files("exports")) == 0
    
    # Проверяем чтение из разных категорий
    track_content = storage_manager.read_file("tracks", "track.mp3")
    image_content = storage_manager.read_file("images", "image.jpg")
    temp_content = storage_manager.read_file("temp", "temp.txt")
    
    assert track_content == test_file_content
    assert image_content == test_file_content
    assert temp_content == test_file_content

def test_error_handling(storage_manager):
    """
    Проверяет обработку ошибок
    """
    # Чтение несуществующего файла
    with pytest.raises(FileNotFoundError):
        storage_manager.read_file("tracks", "nonexistent.mp3")
    
    # Информация о несуществующем файле
    with pytest.raises(FileNotFoundError):
        storage_manager.get_file_info("images", "nonexistent.jpg")
    
    # Удаление несуществующего файла
    result = storage_manager.delete_file("temp", "nonexistent.txt")
    assert result is False
    
    # Список файлов в несуществующей категории
    files = storage_manager.list_files("nonexistent")
    assert len(files) == 0 