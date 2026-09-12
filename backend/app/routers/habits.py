from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Habit
from ..models import Session as SessionModel
from ..schemas import HabitCreate, HabitOut, TreeOut
from ..services.tree import compute_tree

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db)):
    habit = Habit(**payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitOut])
def list_habits(db: Session = Depends(get_db)):
    return db.scalars(select(Habit).order_by(Habit.name)).all()


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="habit not found")
    return habit


@router.get("/{habit_id}/tree", response_model=TreeOut)
def get_habit_tree(
    habit_id: int,
    end_on: date | None = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Árvore de um hábito: intensidade por dia + totais cumulativos.

    Agrega **todo** o histórico do hábito (não só a janela) porque a média móvel
    de 7 dias precisa do *lookback* e o summary é cumulativo por definição.
    """
    habit = db.get(Habit, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="habit not found")

    rows = db.execute(
        select(
            SessionModel.date,
            func.count(SessionModel.id),
            func.sum(SessionModel.duration_min),
        )
        .where(SessionModel.habit_id == habit_id)
        .group_by(SessionModel.date)
    ).all()
    by_date = {row[0]: (int(row[1]), int(row[2] or 0)) for row in rows}

    tree = compute_tree(by_date, end_on=end_on or date.today(), days=days)
    return {"habit": habit, "days": tree["days"], "summary": tree["summary"]}
