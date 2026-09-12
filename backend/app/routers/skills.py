from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Habit
from ..models import Session as SessionModel
from ..schemas import SkillsOut
from ..services.skills import compute_skills

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=SkillsOut)
def list_skills(
    end_on: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Árvores de habilidade + XP derivado das sessões até `end_on`.

    Não há rota de escrita: XP não se escreve, se registra sessão (Spec 002).
    """
    habits = [
        {"id": h.id, "name": h.name, "category": h.category}
        for h in db.scalars(select(Habit).order_by(Habit.name)).all()
    ]
    sessions = [
        {
            "habit_id": s.habit_id,
            "date": s.date,
            "duration_min": s.duration_min,
            "metrics": s.metrics,
            "floor_plan_used": s.floor_plan_used,
        }
        for s in db.scalars(
            select(SessionModel).order_by(SessionModel.date, SessionModel.id)
        ).all()
    ]
    return compute_skills(habits, sessions, end_on=end_on or date.today())