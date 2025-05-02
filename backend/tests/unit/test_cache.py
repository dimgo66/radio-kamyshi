"""
Тесты для проверки функциональности кэширования с эмуляцией Redis
"""
import pytest
import json
import time
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Optional, List, Union

# Эмуляция Redis для тестирования
class MockRedis:
    """
    Эмулятор Redis для тестирования
    """
    def __init__(self):
        self.data = {}
        self.expires = {}
    
    def set(self, key: str, value: str, ex: Optional[int] = None):
        """
        Устанавливает значение по ключу
        
        Args:
            key: Ключ
            value: Значение
            ex: Время истечения срока действия в секундах
        """
        self.data[key] = value
        if ex is not None:
            self.expires[key] = time.time() + ex
        return True
    
    def get(self, key: str) -> Optional[str]:
        """
        Получает значение по ключу
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None, если ключ не найден или истек срок действия
        """
        if key not in self.data:
            return None
            
        # Проверяем срок действия
        if key in self.expires and time.time() > self.expires[key]:
            del self.data[key]
            del self.expires[key]
            return None
            
        return self.data.get(key)
    
    def delete(self, key: str) -> int:
        """
        Удаляет ключ
        
        Args:
            key: Ключ
            
        Returns:
            1, если ключ был удален, 0 в противном случае
        """
        if key in self.data:
            del self.data[key]
            if key in self.expires:
                del self.expires[key]
            return 1
        return 0
    
    def exists(self, key: str) -> int:
        """
        Проверяет существование ключа
        
        Args:
            key: Ключ
            
        Returns:
            1, если ключ существует и не истек срок действия, 0 в противном случае
        """
        if key not in self.data:
            return 0
            
        # Проверяем срок действия
        if key in self.expires and time.time() > self.expires[key]:
            del self.data[key]
            del self.expires[key]
            return 0
            
        return 1
    
    def flushall(self):
        """
        Очищает все данные
        """
        self.data = {}
        self.expires = {}
        return True
    
    def incr(self, key: str, amount: int = 1) -> int:
        """
        Увеличивает значение по ключу
        
        Args:
            key: Ключ
            amount: Величина увеличения
            
        Returns:
            Новое значение
        """
        if key not in self.data:
            self.data[key] = "0"
            
        current = int(self.data[key])
        new_value = current + amount
        self.data[key] = str(new_value)
        return new_value
    
    def decr(self, key: str, amount: int = 1) -> int:
        """
        Уменьшает значение по ключу
        
        Args:
            key: Ключ
            amount: Величина уменьшения
            
        Returns:
            Новое значение
        """
        if key not in self.data:
            self.data[key] = "0"
            
        current = int(self.data[key])
        new_value = current - amount
        self.data[key] = str(new_value)
        return new_value
    
    def lpush(self, key: str, *values) -> int:
        """
        Добавляет значения в начало списка
        
        Args:
            key: Ключ
            values: Значения для добавления
            
        Returns:
            Длина списка после операции
        """
        if key not in self.data:
            self.data[key] = json.dumps([])
            
        current = json.loads(self.data[key])
        for value in values:
            current.insert(0, value)
        
        self.data[key] = json.dumps(current)
        return len(current)
    
    def rpush(self, key: str, *values) -> int:
        """
        Добавляет значения в конец списка
        
        Args:
            key: Ключ
            values: Значения для добавления
            
        Returns:
            Длина списка после операции
        """
        if key not in self.data:
            self.data[key] = json.dumps([])
            
        current = json.loads(self.data[key])
        for value in values:
            current.append(value)
        
        self.data[key] = json.dumps(current)
        return len(current)
    
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        """
        Получает элементы списка в указанном диапазоне
        
        Args:
            key: Ключ
            start: Начальный индекс
            end: Конечный индекс
            
        Returns:
            Список элементов
        """
        if key not in self.data:
            return []
            
        current = json.loads(self.data[key])
        # Обработка отрицательных индексов как в Redis
        if end < 0:
            end = len(current) + end + 1
        # В Redis end включительно, поэтому +1
        return current[start:end+1]
    
    def llen(self, key: str) -> int:
        """
        Получает длину списка
        
        Args:
            key: Ключ
            
        Returns:
            Длина списка
        """
        if key not in self.data:
            return 0
            
        current = json.loads(self.data[key])
        return len(current)
    
    def hset(self, key: str, field: str, value: str) -> int:
        """
        Устанавливает поле в хеш-таблице
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            value: Значение
            
        Returns:
            1, если поле было создано, 0 если обновлено
        """
        if key not in self.data:
            self.data[key] = json.dumps({})
            
        current = json.loads(self.data[key])
        is_new = field not in current
        current[field] = value
        self.data[key] = json.dumps(current)
        return 1 if is_new else 0
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """
        Получает значение поля из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            
        Returns:
            Значение поля или None, если ключ или поле не существует
        """
        if key not in self.data:
            return None
            
        current = json.loads(self.data[key])
        return current.get(field)
    
    def hgetall(self, key: str) -> Dict[str, str]:
        """
        Получает все поля и значения из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            
        Returns:
            Словарь с полями и значениями
        """
        if key not in self.data:
            return {}
            
        return json.loads(self.data[key])
    
    def hdel(self, key: str, field: str) -> int:
        """
        Удаляет поле из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            
        Returns:
            1, если поле было удалено, 0 в противном случае
        """
        if key not in self.data:
            return 0
            
        current = json.loads(self.data[key])
        if field not in current:
            return 0
            
        del current[field]
        self.data[key] = json.dumps(current)
        return 1

# Класс для работы с кэшем
class CacheManager:
    """
    Класс для управления кэшем
    """
    
    def __init__(self, redis_client):
        """
        Инициализация менеджера кэша
        
        Args:
            redis_client: Клиент Redis
        """
        self.redis = redis_client
        self.default_ttl = 3600  # 1 час
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получает значение из кэша
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None, если ключ не найден
        """
        value = self.redis.get(key)
        if value is None:
            return None
            
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Устанавливает значение в кэш
        
        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни в секундах (None для использования значения по умолчанию)
            
        Returns:
            True в случае успеха
        """
        if ttl is None:
            ttl = self.default_ttl
            
        if isinstance(value, (dict, list, tuple, bool, int, float)):
            value = json.dumps(value)
            
        return self.redis.set(key, value, ex=ttl)
    
    def delete(self, key: str) -> bool:
        """
        Удаляет ключ из кэша
        
        Args:
            key: Ключ
            
        Returns:
            True, если ключ был удален, False в противном случае
        """
        return bool(self.redis.delete(key))
    
    def exists(self, key: str) -> bool:
        """
        Проверяет существование ключа
        
        Args:
            key: Ключ
            
        Returns:
            True, если ключ существует, False в противном случае
        """
        return bool(self.redis.exists(key))
    
    def clear(self) -> bool:
        """
        Очищает весь кэш
        
        Returns:
            True в случае успеха
        """
        return self.redis.flushall()
    
    def increment(self, key: str, amount: int = 1) -> int:
        """
        Увеличивает значение счетчика
        
        Args:
            key: Ключ
            amount: Величина увеличения
            
        Returns:
            Новое значение счетчика
        """
        return self.redis.incr(key, amount)
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Уменьшает значение счетчика
        
        Args:
            key: Ключ
            amount: Величина уменьшения
            
        Returns:
            Новое значение счетчика
        """
        return self.redis.decr(key, amount)
    
    def add_to_list(self, key: str, value: Any, prepend: bool = False) -> int:
        """
        Добавляет значение в список
        
        Args:
            key: Ключ
            value: Значение
            prepend: Добавлять в начало списка (True) или в конец (False)
            
        Returns:
            Длина списка после операции
        """
        if isinstance(value, (dict, list, tuple, bool, int, float)):
            value = json.dumps(value)
            
        if prepend:
            return self.redis.lpush(key, value)
        else:
            return self.redis.rpush(key, value)
    
    def get_list(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Получает элементы списка
        
        Args:
            key: Ключ
            start: Начальный индекс
            end: Конечный индекс
            
        Returns:
            Список элементов
        """
        items = self.redis.lrange(key, start, end)
        result = []
        
        for item in items:
            try:
                result.append(json.loads(item))
            except json.JSONDecodeError:
                result.append(item)
                
        return result
    
    def set_hash(self, key: str, field: str, value: Any) -> bool:
        """
        Устанавливает поле в хеш-таблице
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            value: Значение
            
        Returns:
            True в случае успеха
        """
        if isinstance(value, (dict, list, tuple, bool, int, float)):
            value = json.dumps(value)
            
        return bool(self.redis.hset(key, field, value))
    
    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """
        Получает значение поля из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            
        Returns:
            Значение поля или None, если ключ или поле не существует
        """
        value = self.redis.hget(key, field)
        if value is None:
            return None
            
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    def get_all_hash(self, key: str) -> Dict[str, Any]:
        """
        Получает все поля и значения из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            
        Returns:
            Словарь с полями и значениями
        """
        raw_dict = self.redis.hgetall(key)
        result = {}
        
        for field, value in raw_dict.items():
            try:
                result[field] = json.loads(value)
            except json.JSONDecodeError:
                result[field] = value
                
        return result
    
    def delete_hash_field(self, key: str, field: str) -> bool:
        """
        Удаляет поле из хеш-таблицы
        
        Args:
            key: Ключ хеш-таблицы
            field: Поле
            
        Returns:
            True, если поле было удалено, False в противном случае
        """
        return bool(self.redis.hdel(key, field))

# Фикстуры для тестов
@pytest.fixture
def mock_redis():
    """
    Создает экземпляр эмулятора Redis
    """
    return MockRedis()

@pytest.fixture
def cache_manager(mock_redis):
    """
    Создает экземпляр менеджера кэша
    """
    return CacheManager(mock_redis)

# Тесты
def test_set_get(cache_manager):
    """
    Проверяет установку и получение значений
    """
    # Простые типы
    cache_manager.set("string_key", "test_string")
    cache_manager.set("int_key", 42)
    cache_manager.set("float_key", 3.14)
    cache_manager.set("bool_key", True)
    
    # Сложные типы
    cache_manager.set("dict_key", {"name": "Test", "value": 123})
    cache_manager.set("list_key", [1, 2, 3, 4, 5])
    
    # Проверка значений
    assert cache_manager.get("string_key") == "test_string"
    assert cache_manager.get("int_key") == 42
    assert cache_manager.get("float_key") == 3.14
    assert cache_manager.get("bool_key") is True
    assert cache_manager.get("dict_key") == {"name": "Test", "value": 123}
    assert cache_manager.get("list_key") == [1, 2, 3, 4, 5]
    
    # Несуществующий ключ
    assert cache_manager.get("nonexistent_key") is None

def test_delete(cache_manager):
    """
    Проверяет удаление ключей
    """
    # Установка значений
    cache_manager.set("key1", "value1")
    cache_manager.set("key2", "value2")
    
    # Проверка наличия значений
    assert cache_manager.get("key1") == "value1"
    assert cache_manager.get("key2") == "value2"
    
    # Удаление ключа
    assert cache_manager.delete("key1") is True
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") == "value2"
    
    # Удаление несуществующего ключа
    assert cache_manager.delete("nonexistent_key") is False

def test_exists(cache_manager):
    """
    Проверяет проверку существования ключей
    """
    # Установка значения
    cache_manager.set("existing_key", "value")
    
    # Проверка существования
    assert cache_manager.exists("existing_key") is True
    assert cache_manager.exists("nonexistent_key") is False
    
    # Удаление ключа
    cache_manager.delete("existing_key")
    assert cache_manager.exists("existing_key") is False

def test_clear(cache_manager):
    """
    Проверяет очистку кэша
    """
    # Установка нескольких значений
    cache_manager.set("key1", "value1")
    cache_manager.set("key2", "value2")
    cache_manager.set("key3", "value3")
    
    # Проверка наличия значений
    assert cache_manager.get("key1") == "value1"
    assert cache_manager.get("key2") == "value2"
    assert cache_manager.get("key3") == "value3"
    
    # Очистка кэша
    assert cache_manager.clear() is True
    
    # Проверка отсутствия значений
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") is None
    assert cache_manager.get("key3") is None

def test_ttl(cache_manager, mock_redis):
    """
    Проверяет время жизни ключей
    """
    # Устанавливаем значение с маленьким TTL
    cache_manager.set("short_ttl", "value", ttl=1)
    
    # Сразу после установки значение должно существовать
    assert cache_manager.get("short_ttl") == "value"
    
    # Эмулируем задержку
    mock_redis.expires["short_ttl"] = time.time() - 1
    
    # После истечения срока значение должно отсутствовать
    assert cache_manager.get("short_ttl") is None

def test_increment_decrement(cache_manager):
    """
    Проверяет увеличение и уменьшение счетчиков
    """
    # Увеличение несуществующего счетчика
    assert cache_manager.increment("counter") == 1
    assert cache_manager.get("counter") == 1
    
    # Увеличение на определенное значение
    assert cache_manager.increment("counter", 5) == 6
    assert cache_manager.get("counter") == 6
    
    # Уменьшение
    assert cache_manager.decrement("counter") == 5
    assert cache_manager.get("counter") == 5
    
    # Уменьшение на определенное значение
    assert cache_manager.decrement("counter", 3) == 2
    assert cache_manager.get("counter") == 2

def test_lists(cache_manager):
    """
    Проверяет работу со списками
    """
    # Добавление в конец списка
    assert cache_manager.add_to_list("list_key", "item1") == 1
    assert cache_manager.add_to_list("list_key", "item2") == 2
    assert cache_manager.add_to_list("list_key", "item3") == 3
    
    # Получение всего списка
    assert cache_manager.get_list("list_key") == ["item1", "item2", "item3"]
    
    # Получение части списка
    assert cache_manager.get_list("list_key", 1, 2) == ["item2", "item3"]
    
    # Добавление в начало списка
    assert cache_manager.add_to_list("list_key", "item0", prepend=True) == 4
    
    # Проверка обновленного списка
    assert cache_manager.get_list("list_key") == ["item0", "item1", "item2", "item3"]
    
    # Работа с объектами
    cache_manager.add_to_list("object_list", {"id": 1, "name": "Item 1"})
    cache_manager.add_to_list("object_list", {"id": 2, "name": "Item 2"})
    
    items = cache_manager.get_list("object_list")
    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[1]["id"] == 2

def test_hash(cache_manager):
    """
    Проверяет работу с хеш-таблицами
    """
    # Установка полей
    assert cache_manager.set_hash("user:1", "name", "John") is True
    assert cache_manager.set_hash("user:1", "age", 30) is True
    assert cache_manager.set_hash("user:1", "active", True) is True
    assert cache_manager.set_hash("user:1", "data", {"role": "admin", "created": "2023-01-01"}) is True
    
    # Получение отдельных полей
    assert cache_manager.get_hash("user:1", "name") == "John"
    assert cache_manager.get_hash("user:1", "age") == 30
    assert cache_manager.get_hash("user:1", "active") is True
    assert cache_manager.get_hash("user:1", "data") == {"role": "admin", "created": "2023-01-01"}
    
    # Получение всех полей
    all_fields = cache_manager.get_all_hash("user:1")
    assert all_fields["name"] == "John"
    assert all_fields["age"] == 30
    assert all_fields["active"] is True
    assert all_fields["data"] == {"role": "admin", "created": "2023-01-01"}
    
    # Удаление поля
    assert cache_manager.delete_hash_field("user:1", "age") is True
    assert cache_manager.get_hash("user:1", "age") is None
    
    # Удаление несуществующего поля
    assert cache_manager.delete_hash_field("user:1", "nonexistent") is False 