from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Session as SessionModel
from ..schemas import ForestOut
from ..services.forest import compute_forest

router = APIRouter(prefix="/forest", tags=["forest"])


@router.get("", response_model=ForestOut)
def forest(
    end_on: date | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    today = end_on or date.today()
    rows = db.execute(
        select(
            SessionModel.date,
            func.count(func.distinct(SessionModel.habit_id)),
        ).group_by(SessionModel.date)
    ).all()
    completed_by_date = {row[0]: int(row[1]) for row in rows}
    return {"days": compute_forest(completed_by_date, end_on=today, days=days)}