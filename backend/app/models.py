from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    # "rich, not binary": cada hábito declara que métricas rastreia.
    # ex.: {"focus_minutes": "int", "topic": "str", "pomodoros": "int"}
    metrics_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    floor_plan: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    duration_min: Mapped[int] = mapped_column(Integer)
    # dados ricos por hábito: {"focus_minutes": 60, "topic": "SQL Window Functions"}
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    floor_plan_used: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    habit: Mapped["Habit"] = relationship(back_populates="sessions")