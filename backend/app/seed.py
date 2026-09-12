from datetime import date, timedelta

from app.db import SessionLocal, init_db
from app.models import Habit, Session

init_db()
db = SessionLocal()

habits = [
    ("Estudo Tech", "study_tech", {"focus_minutes": "int", "topic": "str"}),
    ("Corrida", "running", {"distance_km": "float", "pace": "str"}),
    ("Leitura", "reading", {"pages": "int"}),
]
ids = {}
for name, category, schema in habits:
    h = Habit(name=name, category=category, metrics_schema=schema,
              floor_plan="abrir editor + 1 parágrafo")
    db.add(h)
    db.flush()
    ids[name] = h.id

today = date.today()
for i in range(14):
    d = today - timedelta(days=13 - i)
    if i % 2 == 0:
        db.add(Session(habit_id=ids["Estudo Tech"], date=d, duration_min=50,
                       metrics={"topic": "SQL"}))
    if i % 3 == 0:
        db.add(Session(habit_id=ids["Corrida"], date=d, duration_min=30,
                       metrics={"distance_km": 5.0}))
    if i % 4 == 0:
        db.add(Session(habit_id=ids["Leitura"], date=d, duration_min=20,
                       metrics={"pages": 12}))

db.commit()
print("Seeded", len(habits), "habits + sessions nos últimos 14 dias")