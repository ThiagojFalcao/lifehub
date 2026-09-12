from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Habit, Session as SessionModel
from ..schemas import SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    if db.get(Habit, payload.habit_id) is None:
        raise HTTPException(status_code=404, detail="habit not found")
    session = SessionModel(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=list[SessionOut])
def list_sessions(habit_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(SessionModel).order_by(SessionModel.date.desc())
    if habit_id is not None:
        stmt = stmt.where(SessionModel.habit_id == habit_id)
    return db.scalars(stmt).all()