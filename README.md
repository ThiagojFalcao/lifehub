# LifeHub

Local-first de telemetria pessoal e progressão de habilidades.

**Vertical slice atual:** tracker de hábitos/sessões (dados ricos, não binários) + visualização "Floresta" (barras diárias + tendência 7d + cores).

## Pré-requisitos
- Python 3.13+ e `uv` (https://docs.astral.sh/uv/)
- Node 20+ e npm

## Rodar

**Backend** (porta 8000):
```bash
cd backend
uv sync
uv run python -m app.seed      # opcional: dados de demonstração
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend** (porta 5173):
```bash
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173.

## Testes
```bash
cd backend && uv run pytest -v
```

## API
- `GET /api/health`
- `GET/POST /api/habits`, `GET /api/habits/{id}`
- `GET/POST /api/sessions?habit_id=`
- `GET /api/forest?days=7&end_on=YYYY-MM-DD`
- `GET /api/habits/{id}/tree?days=30&end_on=YYYY-MM-DD` — Árvore: intensidade por dia + totais cumulativos
- `GET /api/sessions?habit_id=` (ordem determinística: `date desc, id desc`)
- `GET/PUT /api/journal/{date}` (PUT faz upsert; em branco **elimina** a entrada → 404 `Entry removed`)
- `GET /api/journal?limit=30` (últimas entradas, mais recente primeiro)