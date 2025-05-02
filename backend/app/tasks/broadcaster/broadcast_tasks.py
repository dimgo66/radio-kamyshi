import os
import logging
import time
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.celery import celery_app
from app.core.subapse import subapse
from app.crud import program as program_crud
from app.crud import playlist as playlist_crud
from app.models.program import ProgramStatus
from app.db.session import SessionLocal
from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_m3u_playlist(playlist_id: int, output_path: str) -> str:
    """Создает M3U плейлист из треков для Subapse."""
    db = SessionLocal()
    try:
        playlist = playlist_crud.get_playlist_with_tracks(db, playlist_id)
        if not playlist:
            logger.error(f"Playlist with ID {playlist_id} not found")
            return None
        
        m3u_content = "#EXTM3U\n"
        
        # Сортируем треки по позиции
        sorted_tracks = sorted(
            [(pt.position, pt.track) for pt in playlist.playlist_tracks],
            key=lambda x: x[0]
        )
        
        for position, track in sorted_tracks:
            duration_seconds = int(track.duration)
            m3u_content += f"#EXTINF:{duration_seconds},{track.artist} - {track.title}\n"
            m3u_content += f"/audio/input/{os.path.basename(track.file_path)}\n"
        
        # Сохраняем файл
        m3u_path = os.path.join(output_path, f"playlist_{playlist_id}.m3u")
        with open(m3u_path, "w") as f:
            f.write(m3u_content)
        
        return m3u_path
    except Exception as e:
        logger.error(f"Error generating M3U playlist: {e}")
        return None
    finally:
        db.close()


@celery_app.task
def check_scheduled_programs():
    """Проверяет запланированные программы и запускает или останавливает их по расписанию."""
    db = SessionLocal()
    now = datetime.now()
    
    try:
        # Программы, которые должны были запуститься
        programs_to_start = (
            db.query(program_crud.model)
            .filter(
                (program_crud.model.start_time <= now) &
                (program_crud.model.end_time > now) &
                (program_crud.model.status == ProgramStatus.SCHEDULED) &
                (program_crud.model.is_active == True)
            )
            .all()
        )
        
        for program in programs_to_start:
            logger.info(f"Starting program: {program.name} (ID: {program.id})")
            start_program.delay(program.id)
        
        # Программы, которые должны завершиться
        programs_to_stop = (
            db.query(program_crud.model)
            .filter(
                (program_crud.model.end_time <= now) &
                (program_crud.model.status == ProgramStatus.RUNNING) &
                (program_crud.model.is_active == True)
            )
            .all()
        )
        
        for program in programs_to_stop:
            logger.info(f"Stopping program: {program.name} (ID: {program.id})")
            stop_program.delay(program.id)
    
    except Exception as e:
        logger.error(f"Error checking scheduled programs: {e}")
    finally:
        db.close()


@celery_app.task
def start_program(program_id: int):
    """Запускает программу: создает M3U файл и отправляет команду в Subapse."""
    db = SessionLocal()
    
    try:
        program = program_crud.get(db, program_id)
        if not program:
            logger.error(f"Program with ID {program_id} not found")
            return
        
        # Генерируем M3U плейлист
        m3u_path = generate_m3u_playlist(program.playlist_id, settings.PLAYLISTS_DIR)
        if not m3u_path:
            logger.error(f"Failed to generate M3U for program {program_id}")
            return
        
        # Относительный путь для Subapse
        relative_m3u = os.path.join("/audio/playlists", os.path.basename(m3u_path))
        
        # Настройки для Icecast
        icecast_config = {
            "host": settings.ICECAST_HOST,
            "port": settings.ICECAST_PORT,
            "password": settings.ICECAST_SOURCE_PASSWORD
        }
        
        # Запускаем трансляцию через Subapse
        mount_point = f"/radio-{program_id}.mp3"
        try:
            subapse.start_broadcast(
                playlist_path=relative_m3u,
                mount_point=mount_point,
                icecast_config=icecast_config
            )
            logger.info(f"Successfully started broadcast for program {program_id}")
            
            # Обновляем статус программы
            program.status = ProgramStatus.RUNNING
            db.add(program)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to start broadcast: {e}")
            return
    
    except Exception as e:
        logger.error(f"Error starting program {program_id}: {e}")
    finally:
        db.close()


@celery_app.task
def stop_program(program_id: int):
    """Останавливает программу и обновляет ее статус."""
    db = SessionLocal()
    
    try:
        program = program_crud.get(db, program_id)
        if not program:
            logger.error(f"Program with ID {program_id} not found")
            return
        
        # Останавливаем трансляцию через Subapse
        mount_point = f"/radio-{program_id}.mp3"
        try:
            subapse.stop_broadcast(mount_point=mount_point)
            logger.info(f"Successfully stopped broadcast for program {program_id}")
            
            # Обновляем статус программы
            program.status = ProgramStatus.COMPLETED
            db.add(program)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to stop broadcast: {e}")
            return
    
    except Exception as e:
        logger.error(f"Error stopping program {program_id}: {e}")
    finally:
        db.close()


@celery_app.task
def cleanup_old_programs():
    """Очищает старые плейлисты и обновляет статусы завершенных программ."""
    db = SessionLocal()
    past_day = datetime.now() - timedelta(days=1)
    
    try:
        # Находим все программы, которые завершились в прошлом
        old_programs = (
            db.query(program_crud.model)
            .filter(
                (program_crud.model.end_time < past_day) &
                (program_crud.model.status.in_([ProgramStatus.RUNNING, ProgramStatus.SCHEDULED]))
            )
            .all()
        )
        
        for program in old_programs:
            logger.info(f"Cleaning up old program: {program.name} (ID: {program.id})")
            program.status = ProgramStatus.COMPLETED
            db.add(program)
        
        db.commit()
        
        # Очищаем старые M3U файлы
        playlists_dir = settings.PLAYLISTS_DIR
        if os.path.exists(playlists_dir):
            for filename in os.listdir(playlists_dir):
                if filename.endswith(".m3u"):
                    file_path = os.path.join(playlists_dir, filename)
                    file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_modified < past_day:
                        logger.info(f"Removing old playlist file: {file_path}")
                        os.remove(file_path)
    
    except Exception as e:
        logger.error(f"Error cleaning up old programs: {e}")
    finally:
        db.close() 