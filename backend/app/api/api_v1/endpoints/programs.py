from datetime import datetime, date
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.dependencies import get_db, get_current_active_user
from app.models.program import ProgramStatus
from app.api import deps
from app.crud import crud_program
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramInDB,
    ProgramScheduleCreate,
    ProgramScheduleUpdate,
    ProgramScheduleInDB
)

router = APIRouter()


@router.get("/", response_model=List[ProgramInDB])
def get_programs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Получить список всех программ.
    """
    return crud_program.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=ProgramInDB)
def create_program(
    *,
    db: Session = Depends(deps.get_db),
    program_in: ProgramCreate
):
    """
    Создать новую программу.
    """
    return crud_program.create(db, obj_in=program_in)


@router.get("/{program_id}", response_model=ProgramInDB)
def get_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: int
):
    """
    Получить программу по ID.
    """
    program = crud_program.get(db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return program


@router.put("/{program_id}", response_model=ProgramInDB)
def update_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: int,
    program_in: ProgramUpdate
):
    """
    Обновить программу.
    """
    program = crud_program.get(db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return crud_program.update(db, db_obj=program, obj_in=program_in)


@router.delete("/{program_id}")
def delete_program(
    *,
    db: Session = Depends(deps.get_db),
    program_id: int
):
    """
    Удалить программу.
    """
    program = crud_program.get(db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    crud_program.remove(db, id=program_id)
    return {"ok": True}


@router.get("/schedules/", response_model=List[ProgramScheduleInDB])
def get_schedules(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Получить список всех расписаний.
    """
    return crud_program.get_schedules(db, skip=skip, limit=limit)


@router.post("/schedules/", response_model=ProgramScheduleInDB)
def create_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_in: ProgramScheduleCreate
):
    """
    Создать новое расписание.
    """
    return crud_program.create_schedule(db, obj_in=schedule_in)


@router.put("/schedules/{schedule_id}", response_model=ProgramScheduleInDB)
def update_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_id: int,
    schedule_in: ProgramScheduleUpdate
):
    """
    Обновить расписание.
    """
    schedule = crud_program.get_schedule(db, id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    return crud_program.update_schedule(db, db_obj=schedule, obj_in=schedule_in)


@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_id: int
):
    """
    Удалить расписание.
    """
    schedule = crud_program.get_schedule(db, id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    crud_program.remove_schedule(db, id=schedule_id)
    return {"ok": True}


@router.get("/current/", response_model=Optional[ProgramInDB])
def get_current_program(
    db: Session = Depends(deps.get_db)
):
    """
    Получить текущую программу в эфире.
    """
    return crud_program.get_current_program(db)


@router.get("/upcoming/", response_model=List[ProgramInDB])
def get_upcoming_programs(
    db: Session = Depends(deps.get_db),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Получить список предстоящих программ.
    """
    return crud_program.get_upcoming_programs(db, limit=limit)


@router.get("/calendar/{year}/{month}/{day}", response_model=List[schemas.Program])
def get_programs_by_day(
    *,
    db: Session = Depends(get_db),
    year: int,
    month: int,
    day: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить программы на определенный день.
    """
    try:
        target_date = date(year, month, day)
        target_datetime = datetime.combine(target_date, datetime.min.time())
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверная дата")
    
    programs = crud.program.get_programs_by_day(db, target_datetime)
    # Фильтруем программы по пользователю
    user_programs = [prog for prog in programs if prog.user_id == current_user.id]
    
    return user_programs


@router.get("/current", response_model=schemas.Program)
def get_current_program_old(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить текущую активную программу.
    """
    # Примечание: здесь мы возвращаем текущую программу конкретного пользователя,
    # а в реальности может понадобиться получать текущую программу станции независимо от владельца
    program = crud.program.get_current_program(db)
    
    if not program or program.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Нет текущих активных программ")
    
    return program


@router.get("/next", response_model=schemas.Program)
def get_next_program(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить следующую запланированную программу.
    """
    program = crud.program.get_next_scheduled_program(db)
    
    if not program or program.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Нет запланированных программ")
    
    return program


@router.get("/{program_id}", response_model=schemas.Program)
def read_program(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Получить программу по ID.
    """
    program = crud.program.get(db=db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    if program.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для доступа к этой программе"
        )
    return program


@router.put("/{program_id}", response_model=schemas.Program)
def update_program_old(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    program_in: schemas.ProgramUpdate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Обновить программу.
    """
    program = crud.program.get(db=db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    if program.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для изменения этой программы"
        )
    
    # Проверяем возможность изменения программы
    if program.status == ProgramStatus.RUNNING:
        raise HTTPException(
            status_code=400, detail="Нельзя изменить запущенную программу"
        )
    
    # Если меняется плейлист, проверяем его существование и владельца
    if program_in.playlist_id is not None:
        playlist = crud.playlist.get(db=db, id=program_in.playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Плейлист не найден")
        if playlist.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Вы не можете использовать этот плейлист"
            )
    
    program = crud.program.update(db=db, db_obj=program, obj_in=program_in)
    return program


@router.delete("/{program_id}", response_model=schemas.Program)
def delete_program_old(
    *,
    db: Session = Depends(get_db),
    program_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить программу.
    """
    program = crud.program.get(db=db, id=program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    if program.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для удаления этой программы"
        )
    
    # Проверяем возможность удаления программы
    if program.status == ProgramStatus.RUNNING:
        raise HTTPException(
            status_code=400, detail="Нельзя удалить запущенную программу"
        )
    
    program = crud.program.remove(db=db, id=program_id)
    return program 