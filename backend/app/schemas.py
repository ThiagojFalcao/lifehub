from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    metrics_schema: dict = Field(default_factory=dict)
    floor_plan: str | None = Field(default=None, max_length=300)


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    metrics_schema: dict
    floor_plan: str | None
    created_at: datetime


class SessionCreate(BaseModel):
    habit_id: int
    date: date
    duration_min: int = Field(gt=0)
    metrics: dict = Field(default_factory=dict)
    floor_plan_used: bool = False
    notes: str | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    date: date
    duration_min: int
    metrics: dict
    floor_plan_used: bool
    notes: str | None
    created_at: datetime


class ForestDay(BaseModel):
    date: date
    completed: int
    avg_7d: float
    color: str


class ForestOut(BaseModel):
    days: list[ForestDay]


class TreeDay(BaseModel):
    date: date
    sessions: int
    duration_min: int
    avg_7d_min: float
    color: str


class TreeSummary(BaseModel):
    """Totais cumulativos do hábito (todo o histórico, não só a janela)."""

    total_sessions: int
    total_min: int
    total_hours: float
    active_days: int
    current_streak: int
    best_streak: int
    avg_min_per_active_day: float


class TreeOut(BaseModel):
    habit: HabitOut
    days: list[TreeDay]
    summary: TreeSummary


class JournalEntryUpsert(BaseModel):
    """Payload do PUT /api/journal/{date} (upsert)."""

    content: str = ""
    mood: str | None = Field(default=None, max_length=30)
    tags: list[str] = Field(default_factory=list)


class JournalEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    content: str
    mood: str | None
    tags: list[str]
    updated_at: datetime