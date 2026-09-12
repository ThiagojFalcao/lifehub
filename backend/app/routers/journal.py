from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import JournalEntry
from ..schemas import JournalEntryOut, JournalEntryUpsert

router = APIRouter(prefix="/journal", tags=["journal"])


def _get_or_404(db: Session, d: date) -> JournalEntry:
    entry = db.scalar(select(JournalEntry).where(JournalEntry.date == d))
    if entry is None:
        raise HTTPException(status_code=404, detail="No journal entry for this date")
    return entry


@router.put("/{entry_date}", response_model=JournalEntryOut)
def upsert_entry(entry_date: date, payload: JournalEntryUpsert, db: Session = Depends(get_db)):
    """Crea o actualiza la entrada del journal para una fecha (upsert).

    Un PUT con `content`, `mood` y `tags` vacíos elimina la entrada
    (para que vaciar el editor borre, como en un diario físico).
    """
    entry = db.scalar(select(JournalEntry).where(JournalEntry.date == entry_date))
    is_blank = not payload.content.strip() and not payload.mood and not payload.tags

    if entry is None and is_blank:
        # No hay nada que guardar: no crear entrada vacía.
        raise HTTPException(status_code=404, detail="Nothing to save")

    if entry is None:
        entry = JournalEntry(
            date=entry_date,
            content=payload.content,
            mood=payload.mood,
            tags=list(payload.tags),
        )
        db.add(entry)
    elif is_blank:
        db.delete(entry)
        db.commit()
        raise HTTPException(status_code=404, detail="Entry removed")
    else:
        entry.content = payload.content
        entry.mood = payload.mood
        entry.tags = list(payload.tags)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=list[JournalEntryOut])
def list_entries(
    limit: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Lista entradas ordenadas por fecha desc (más reciente primero)."""
    stmt = (
        select(JournalEntry)
        .order_by(JournalEntry.date.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


@router.get("/{entry_date}", response_model=JournalEntryOut)
def get_entry(entry_date: date, db: Session = Depends(get_db)):
    """Devuelve la entrada de una fecha; 404 si no existe."""
    return _get_or_404(db, entry_date)