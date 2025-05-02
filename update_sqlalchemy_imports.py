#!/usr/bin/env python3
"""
Скрипт для обновления устаревших импортов SQLAlchemy во всех файлах проекта
"""
import os
import re

def update_file(file_path):
    """Обновляет импорты SQLAlchemy в указанном файле"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    updated = False
    
    # Проверяем, есть ли устаревший импорт declarative_base
    if 'sqlalchemy.ext.declarative import declarative_base' in content:
        print(f"Обновление импорта declarative_base в {file_path}")
        
        # Если уже есть импорт из sqlalchemy.orm, добавляем к нему declarative_base
        if 'from sqlalchemy.orm import ' in content:
            content = re.sub(
                r'from sqlalchemy.orm import (.*?)\n',
                r'from sqlalchemy.orm import \1, declarative_base\n',
                content
            )
            # Удаляем строку с устаревшим импортом
            content = re.sub(
                r'from sqlalchemy.ext.declarative import declarative_base\n',
                '',
                content
            )
        else:
            # Заменяем импорт напрямую
            content = content.replace(
                'from sqlalchemy.ext.declarative import declarative_base',
                'from sqlalchemy.orm import declarative_base'
            )
        
        updated = True
    
    # Проверяем, есть ли устаревший импорт sessionmaker
    if 'sqlalchemy.ext.declarative import sessionmaker' in content:
        print(f"Обновление импорта sessionmaker в {file_path}")
        
        # Если уже есть импорт из sqlalchemy.orm, добавляем к нему sessionmaker
        if 'from sqlalchemy.orm import ' in content:
            content = re.sub(
                r'from sqlalchemy.orm import (.*?)\n',
                r'from sqlalchemy.orm import \1, sessionmaker\n',
                content
            )
            # Удаляем строку с устаревшим импортом
            content = re.sub(
                r'from sqlalchemy.ext.declarative import sessionmaker\n',
                '',
                content
            )
        else:
            # Заменяем импорт напрямую
            content = content.replace(
                'from sqlalchemy.ext.declarative import sessionmaker',
                'from sqlalchemy.orm import sessionmaker'
            )
        
        updated = True
    
    # Записываем обновленный контент, если были изменения
    if updated:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    return False

def scan_directory(directory):
    """Сканирует директорию и обновляет все Python файлы"""
    updated_files = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    updated_files += 1
    
    return updated_files

def main():
    """Основная функция"""
    total_updated = 0
    
    # Обновляем файлы в backend
    backend_dir = os.path.join('backend')
    if os.path.exists(backend_dir):
        updated = scan_directory(backend_dir)
        print(f"Обновлено файлов в backend: {updated}")
        total_updated += updated
    
    # Обновляем дополнительные файлы в корне проекта
    for file in os.listdir('.'):
        if file.endswith('.py'):
            file_path = os.path.join('.', file)
            if update_file(file_path):
                total_updated += 1
    
    print(f"Всего обновлено файлов: {total_updated}")

if __name__ == '__main__':
    main() 