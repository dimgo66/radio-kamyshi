from typing import List, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.crud.base import CRUDBase
from app.models.program import Program, ProgramStatus, ProgramSchedule
from app.schemas.program import ProgramCreate, ProgramUpdate, ProgramScheduleCreate, ProgramScheduleUpdate


class CRUDProgram(CRUDBase[Program, ProgramCreate, ProgramUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: ProgramCreate, user_id: int
    ) -> Program:
        db_obj = Program(
            name=obj_in.name,
            description=obj_in.description,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            playlist_id=obj_in.playlist_id,
            user_id=user_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Program]:
        return (
            db.query(self.model)
            .filter(Program.user_id == user_id)
            .order_by(desc(Program.start_time))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_current_program(self, db: Session) -> Optional[Program]:
        now = datetime.utcnow()
        current_schedule = db.query(ProgramSchedule).filter(
            and_(
                ProgramSchedule.start_time <= now,
                ProgramSchedule.end_time > now,
                ProgramSchedule.is_active == True
            )
        ).order_by(ProgramSchedule.priority.desc()).first()

        if current_schedule:
            return db.query(Program).filter(Program.id == current_schedule.program_id).first()
        return None

    def get_next_scheduled_program(self, db: Session) -> Optional[Program]:
        now = datetime.now()
        return (
            db.query(Program)
            .filter(
                and_(
                    Program.start_time > now,
                    Program.status == ProgramStatus.SCHEDULED,
                    Program.is_active == True
                )
            )
            .order_by(Program.start_time)
            .first()
        )
    
    def get_programs_by_day(self, db: Session, date: datetime) -> List[Program]:
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return (
            db.query(Program)
            .filter(
                and_(
                    Program.start_time >= start_of_day,
                    Program.start_time <= end_of_day,
                    Program.is_active == True
                )
            )
            .order_by(Program.start_time)
            .all()
        )

    def create_schedule(
        self, db: Session, *, obj_in: ProgramScheduleCreate
    ) -> ProgramSchedule:
        db_obj = ProgramSchedule(
            program_id=obj_in.program_id,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            repeat_type=obj_in.repeat_type,
            repeat_days=json.dumps(obj_in.repeat_days) if obj_in.repeat_days else None,
            priority=obj_in.priority,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_schedule(
        self,
        db: Session,
        *,
        db_obj: ProgramSchedule,
        obj_in: ProgramScheduleUpdate
    ) -> ProgramSchedule:
        update_data = obj_in.dict(exclude_unset=True)
        if "repeat_days" in update_data and update_data["repeat_days"] is not None:
            update_data["repeat_days"] = json.dumps(update_data["repeat_days"])
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_schedule(self, db: Session, id: int) -> Optional[ProgramSchedule]:
        return db.query(ProgramSchedule).filter(ProgramSchedule.id == id).first()

    def get_schedules(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ProgramSchedule]:
        return db.query(ProgramSchedule).offset(skip).limit(limit).all()

    def remove_schedule(self, db: Session, *, id: int) -> ProgramSchedule:
        obj = db.query(ProgramSchedule).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_upcoming_programs(
        self, db: Session, *, limit: int = 5
    ) -> List[Program]:
        now = datetime.utcnow()
        upcoming_schedules = db.query(ProgramSchedule).filter(
            and_(
                ProgramSchedule.start_time > now,
                ProgramSchedule.is_active == True
            )
        ).order_by(ProgramSchedule.start_time).limit(limit).all()

        program_ids = [schedule.program_id for schedule in upcoming_schedules]
        return db.query(Program).filter(Program.id.in_(program_ids)).all()

    def get_week_schedule(
        self, db: Session, *, start_date: datetime
    ) -> List[ProgramSchedule]:
        end_date = start_date + timedelta(days=7)
        return db.query(ProgramSchedule).filter(
            and_(
                ProgramSchedule.start_time >= start_date,
                ProgramSchedule.start_time < end_date,
                ProgramSchedule.is_active == True
            )
        ).order_by(ProgramSchedule.start_time).all()


program = CRUDProgram(Program) 