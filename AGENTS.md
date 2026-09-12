# AGENTS.md — LifeHub

Contexto técnico para desenvolvedores humanos e agentes de IA.

## O que é

LifeHub é um sistema **local-first** de telemetria pessoal e progressão de habilidades:
tracker de hábitos não-binários, visualização "Floresta", skill trees, XP, journal e coach IA.
Construção incremental, feature por feature.

## Stack

- **Backend:** Python 3.13 · FastAPI · SQLAlchemy 2.0 · SQLite
- **Frontend:** Svelte 5 · Vite
- **Gerenciamento:** `uv` (Python), `npm` (frontend)
- **CI:** GitHub Actions (ruff + pytest + build)

## Layout

```
backend/        -> app FastAPI (app/, tests/)
frontend/       -> app Svelte (src/)
docs/specs/     -> specs de features (SDD leve)
.hermes/plans/  -> planos de trabalho do agente (NÃO versionado)
```

## Comandos

Backend (a partir de `backend/`):

- `uv sync` — instala deps
- `uv run pytest -v` — testes
- `uv run ruff check .` — lint
- `uv run uvicorn app.main:app --reload --port 8000` — servidor

Frontend (a partir de `frontend/`):

- `npm install` / `npm ci`
- `npm run dev` — dev server (proxy `/api` -> 8000)
- `npm run build` — build de produção

## Como retomar (ao iniciar qualquer sessão)

1. Ler `PROGRESS.md` (estado atual + próximo passo + decisões em aberto).
2. Ler este arquivo e `CONTRIBUTING.md` se não estiver em contexto.
3. `git log --oneline -20` para a história recente.
4. Nunca re-decidir algo já registrado como fechado — avançar a partir do `Próximo passo`.

## Convenções

- Mensagens de commit em **Conventional Commits** (ver `CONTRIBUTING.md`).
- `main` protegida; merge via PR com **squash**.
- Código novo segue **TDD** para lógica; UI manual/visual.
- Decisões de arquitetura vão para `docs/adr/`.
- Nunca commitar segredos; `*.db` e `.env` estão no `.gitignore`.