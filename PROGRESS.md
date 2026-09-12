# PROGRESS.md — LifeHub

> **Flight recorder del proyecto.** Este archivo es la fuente de verdad del "dónde estamos".
> Actualizado al final de **toda sesión de trabajo** — y reabierto en **toda sesión nueva**.
>
> **Orden de lectura en una sesión nueva:** `PROGRESS.md` → `AGENTS.md` → `git log --oneline -20`.
> Regla de actualización en `CONTRIBUTING.md`.

---

## 1 · Visión general

**LifeHub** — sistema local-first de telemetría personal y progresión de habilidades:
tracker de hábitos no-binarios, visualización "Floresta", skill trees, XP, journal y coach IA.
Construcción **incremental, feature por feature**, con TDD y CI desde el inicio.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2.0 · SQLite · Svelte 5 · Vite · GitHub Actions.
**Repo:** privado en GitHub (`ThiagojFalcao/lifehub`).

---

## 2 · Roadmap (milestones / features)

| # | Feature | Spec | Status |
|---|---------|------|--------|
| M0 | Fundación: git init, `.gitignore`, convenciones, AGENTS, CI | — | ✅ concluido |
| F1 | Vertical slice: tracker de hábitos + visualización Floresta | `docs/specs/000-vertical-slice.md` | ✅ 96% — solo queda verificación visual manual |
| F2 | Journal + nota diaria (híbrido) | `docs/specs/00X-journal.md` | ⬛ backlog |
| F3 | Skill trees (Tech / Ejercicio / Hidratación) + XP | — | ⬛ backlog |
| F4 | RAG / Coach IA | — | ⬛ backlog |
| F5 | Boss Battles | — | ⬛ backlog |
| F6 | git auto-sync + Docker (portabilidad) | — | ⬛ backlog |

> ⬜ = próximo / en desarrollo · ⬛ = backlog (objetivo del usuario: subir feature por feature en GitHub).

---

## 3 · Estado actual

**Milestone 0 — Fundación: ✅ CONCLUIDO.**

- [x] `git init` + `.gitignore` (backend/frontend/db/env)
- [x] `CONTRIBUTING.md` — convenciones de commit/PR + flight recorder
- [x] `AGENTS.md` — contexto técnico + "cómo retomar"
- [x] `README.md`
- [x] `docs/specs/000-vertical-slice.md` — spec de la F1
- [x] `.github/workflows/ci.yml` — ruff + pytest + build en todo PR
- [x] Identidad git: `Thiago Falcão <167378662+ThiagojFalcao@users.noreply.github.com>`
- [x] `gh` CLI instalado (v2.100.0) + autenticado + repo privado creado + push inicial

**Feature 1 — Vertical slice (tracker + Floresta): 🔄 95% (C y D hechas, verificación visual manual pendiente).**

- [x] **Parte A** — scaffold: `backend/pyproject.toml` (uv), frontend Vite+Svelte 5.
- [x] **Parte B** — backend TDD completo: models, db, schemas, routers (habits/sessions/forest), servicio puro `compute_forest`. **10 tests pasando**, `ruff check` limpio.
- [x] **Parte C** — frontend: proxy Vite + `api.js` + `ForestChart.svelte` (SVG con `$derived` reactivo) + `App.svelte` (dashboard). Build limpio sin warnings.
- [x] **Parte D** — seed demo + smoke test e2e (POST sesión vía proxy + Floresta actualizada en vivo) + README final.
- [ ] **Verificación visual manual** — abrir `http://localhost:5173` y confirmar que el gráfico SVG se ve (barras + línea azul). Yo lo dejé verificado por código (SVG compilado, API respondiendo), pero el pane de preview no renderiza localhost.

---

## 4 · Próximo paso

1. **Verificación visual opcional**: `cd frontend && npm run dev` → abrir `http://localhost:5173` (con backend en 8000).
2. **Proteger `main`** en GitHub (Settings → Branches → solo via PR) — sigue pendiente.
3. **F2 — Journal** (híbrido markdown + frontmatter + endpoint), siguiendo el roadmap.

> Comando de partida:
> ```bash
> cd /opt/data/lifehub-app/backend && uv run uvicorn app.main:app --reload --port 8000 &
> cd /opt/data/lifehub-app/frontend && npm run dev
> ```

---

## 5 · En abierto (decisiones pendientes)

- [ ] Proteger `main` en GitHub (protección de rama solo-PR).
- [ ] Verificación visual manual de la UI (opcional, ya cubierta por smoke e2e).

---

## 6 · Conectar al GitHub (checklist)

| Paso | Comando / acción | Estado |
|------|------------------|--------|
| 1. Autenticar `gh` | `gh auth login` (browser → pegar código) | ✅ en sesión anterior |
| 2. Crear repo privado | `gh repo create lifehub --private --source=. --remote=origin --push` | ✅ `ThiagojFalcao/lifehub` |
| 3. Push inicial | (cubierto por el `--push` de arriba) | ✅ push continuo en cada commit |
| 4. Proteger `main` | GitHub → Settings → Branches → protección (solo vía PR) | ❌ pendiente |

---

## 7 · Historial de sesiones

<!-- Formato: "- YYYY-MM-DD — resumen corto de lo que se hizo y de lo que quedó pendiente". -->

- 2026-09-12 — **Sesión 2 (Frontend + integración):** commit de la Task C1 interrumpida (proxy Vite + `api.js`); C2 `ForestChart.svelte` (corregido a `$derived` para reactividad sin warnings); C3 `App.svelte` dashboard completo; Parte D: seed demo, smoke e2e real (health, habits, forest, POST sesión vía proxy Vite → Floresta se actualizó de rojo a amarillo en vivo, luego cleanup), README final. Backend 10/10 tests verdes. Todo pusheado a `origin/main`. Pendiente: protección de `main` en GitHub y verificación visual manual.
- 2026-09-11 — **Sesión 1 (Fundación + Backend):** M0 concluido (git init, convenciones, AGENTS, CI, gh auth, repo `ThiagojFalcao/lifehub` creado + push inicial). Parte B backend TDD: models, db, conftest, schemas, routers habits/sessions/forest, `compute_forest`, 10 tests verdes.