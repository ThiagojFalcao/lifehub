from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Habit
from ..models import Session as SessionModel
from ..schemas import SessionCreate, SessionOut
from ..services.metrics import validate_metrics

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    habit = db.get(Habit, payload.habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="habit not found")

    # O schema do hábito é dica, não jaula: coage o que ele declara e recusa
    # só o que ele declara e foi violado (métricas livres passam).
    try:
        metrics = validate_metrics(payload.metrics, habit.metrics_schema)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    session = SessionModel(**{**payload.model_dump(), "metrics": metrics})
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