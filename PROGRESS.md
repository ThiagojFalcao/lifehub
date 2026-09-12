# PROGRESS.md — LifeHub

> **Flight recorder del proyecto.** Este archivo es la fuente de verdad del "dónde estamos".
> Actualizado al final de **toda sesión de trabajo** — y reabierto en **toda sesión nueva**.
>
> **Orden de lectura en una sesión nueva:** `PROGRESS.md` → `AGENTS.md` → `git log --oneline -20`.
> Regla de actualización en `CONTRIBUTING.md`.
>
> ⚠️ **Idioma:** o projeto migrou para **pt-BR** (UI, código e docs). As entradas antigas
> deste arquivo estão em espanhol e ficam como registro histórico; **todo texto novo é em pt-BR**.

---

## 1 · Visão geral

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
| F1 | Vertical slice: tracker de hábitos + visualización Floresta | `docs/specs/000-vertical-slice.md` | ✅ concluido (95% + rediseño Linear dark) |
| F2 | Journal + nota diária (híbrido) | — | ✅ concluido (backend+UI, 16 tests) |
| F2.5 | Telemetria rica: **Árvore** + Galhos (`metrics_schema` vivo) | `docs/specs/001-telemetria-rica-arvore-galhos.md` | ✅ concluído (backend + UI, 65 tests) |
| F3 | Skill trees (Tech / Ejercicio / Hidratación / Geral) + XP | `docs/specs/002-skill-trees-xp.md` | ✅ concluído (backend + UI, 95 tests) |
| F4 | RAG / Coach IA | — | ⬛ backlog |
| F5 | Boss Battles | — | ⬛ backlog |
| F6 | git auto-sync + Docker (portabilidad) | — | ⬛ backlog |

> ⬜ = próximo / en desarrollo · ⬛ = backlog (objetivo del usuario: subir feature por feature en GitHub).

---

## 3 · Estado atual

**Milestone 0 — Fundación: ✅ CONCLUIDO.**

- [x] `git init` + `.gitignore` (backend/frontend/db/env)
- [x] `CONTRIBUTING.md` — convenciones de commit/PR + flight recorder
- [x] `AGENTS.md` — contexto técnico + "cómo retomar"
- [x] `README.md`
- [x] `docs/specs/000-vertical-slice.md` — spec de la F1
- [x] `.github/workflows/ci.yml` — ruff + pytest + build en todo PR
- [x] Identidad git: `Thiago Falcão <167378662+ThiagojFalcao@users.noreply.github.com>`
- [x] `gh` CLI instalado (v2.100.0) + autenticado + repo privado creado + push inicial

**Feature 1 — Vertical slice (tracker + Floresta): ✅ CONCLUIDO.**

- [x] **Parte A** — scaffold: `backend/pyproject.toml` (uv), frontend Vite+Svelte 5.
- [x] **Parte B** — backend TDD: models, db, schemas, routers (habits/sessions/forest), serviço puro `compute_forest`. **10 tests pasando**, `ruff check` limpio.
- [x] **Parte C** — frontend: proxy Vite + `api.js` + `ForestChart.svelte` (SVG, `$derived`) + `App.svelte` dashboard.
- [x] **Parte D** — seed demo + smoke e2e + README final.
- [x] **Rediseño UI** — sistema Linear dark (Inter cv01/ss03 + JetBrains Mono, indigo `#5e6ad2`, borders semitransparentes, luminance stacking). Slop score 4/10 → 0/10.

**Feature 2 — Journal (híbrido markdown + frontmatter): ✅ CONCLUIDO.**

- [x] **Backend** (TDD): modelo `JournalEntry` (1 por fecha, unique), schemas, router `/api/journal` — PUT upsert, GET list (ordenado desc + `?limit=`), GET por fecha (404 si no existe), PUT vacío elimina. **6 tests** nuevos (suite total: 16).
- [x] **Frontend** (Svelte 5, design Linear): panel Journal no dashboard — editor markdown (textarea mono), select de mood, tags, lista "Entradas recientes" clicable (carga la entrada no editor).

**Feature 2.5 — Telemetria rica (Árvore + Galhos): ✅ CONCLUÍDO.**

- [x] **Backend** (TDD, commitado nas sessões 4): `GET /api/habits/{id}/tree?days=&end_on=` (intensidade por dia + média móvel 7d + cores + `summary` cumulativo), validação/coerção de `metrics` da sessão contra o `metrics_schema` do hábito (métrica declarada violada → 422 com motivo legível; métrica livre passa), ordem determinística em `GET /api/sessions` (`date desc, id desc`). **65 tests**, ruff limpo.
- [x] **Frontend**: shell com **abas** (`Floresta` / `Árvore` / `Journal`) em pt-BR — `ArvoreArea.svelte` (seletor de hábito, `TreeChart`, progresso cumulativo, lista de Galhos com métricas), `JournalArea.svelte` (nota diária markdown + frontmatter, histórico clicável), `MetricsFields.svelte` e `NovoHabitPanel.svelte` (campos de métrica gerados do `metrics_schema`), `RegistrarPanel.svelte` (registro de sessão + floor plan). Build de produção **sem warnings de a11y**.
- [x] **Bug corrigido pelo e2e**: limpar o editor do diário e salvar mostrava `Entry removed` como erro vermelho — a remoção (404 intencional do backend) agora é tratada como sucesso ("Entrada removida").
- [x] **Harness de verificação viva**: `backend/scripts/e2e_verificacao.py` (HTTP real, banco isolado em `/tmp`, 30 checagens).

**Feature 3 — Skill trees + XP (derivado): ✅ CONCLUÍDO.**

- [x] **Spec** `docs/specs/002-skill-trees-xp.md` aprovada (2026-09-12) — XP **derivado** das sessões (sem coluna nova, sem migração), fórmula tunável, curva triangular, categoria → árvore com fallback `Geral`.
- [x] **Backend** (TDD): `app/services/skills.py` — `xp_of_session`, `nivel_de_xp` (curva triangular), `tree_for_category`, `compute_skills` (streak por hábito em passada ordenada, breakdown `base`/`floor_plan`/`metrics`/`streak`, arredondamento half-up no total), schemas `SkillsOut`/`SkillTreeOut`/`SkillHabitOut`/`SkillBreakdown`, router `GET /api/skills?end_on=` + registro no `main`. **30 testes novos** (25 unit + 5 API) → suíte **95 passed**, ruff limpo.
- [x] **Frontend**: aba **Habilidades** (`HabilidadesArea.svelte` + CSS `.level-bar`/`.tree-card` etc.) — nível geral com barra de progresso, regras de XP, grid de cards por árvore (Tech / Exercício / Hidratação / Geral) com level, breakdown e hábitos. Build **sem warnings**.
- [x] **E2E vivo**: harness cobre `/api/skills` (ordem das árvores, total_xp, breakdown fecha, banco vazio → 200, instância real + proxy) — **todas as checagens passam**.

---

## 4 · Próximo passo

1. **F4 — RAG / Coach IA**: embeddings locais + Openrouter (chat), respostas com contexto dos dados (journal + hábitos + sessões). É a feature de maior valor percebido depois do XP.
2. **Proteger `main`** no GitHub (Settings → Branches → só via PR) — segue pendente (hoje o push vai direto para `main`).
3. Verificação **visual** da aba Habilidades no navegador (Floresta / Árvore / Journal / Habilidades) — o e2e cobre a API, não os olhos.

> Comandos que funcionam **neste ambiente** (WSL, `/opt/data/lifehub-app`):
> ```bash
> # backend (porta 8000) — .venv já existe em backend/.venv
> cd /opt/data/lifehub-app/backend && ./.venv/bin/python -m uvicorn app.main:app --port 8000
>
> # frontend (porta 5173, proxy /api -> :8000)
> cd /opt/data/lifehub-app/frontend && HOME=/opt/data npm run dev
>
> # verificação viva de ponta a ponta (não mexe no banco do usuário)
> cd /opt/data/lifehub-app && backend/.venv/bin/python backend/scripts/e2e_verificacao.py
> ```

---

## 5 · Em aberto (decisões pendentes)

- [ ] Proteger `main` en GitHub (protección de rama solo-PR).
- [ ] Verificación visual manual de la UI (opcional, ya cubierta por smoke e2e).

---

## 6 · Conectar ao GitHub (checklist)

| Paso | Comando / acción | Estado |
|------|------------------|--------|
| 1. Autenticar `gh` | `gh auth login` (browser → pegar código) | ✅ en sesión anterior |
| 2. Crear repo privado | `gh repo create lifehub --private --source=. --remote=origin --push` | ✅ `ThiagojFalcao/lifehub` |
| 3. Push inicial | (cubierto por el `--push` de arriba) | ✅ push continuo en cada commit |
| 4. Proteger `main` | GitHub → Settings → Branches → protección (solo vía PR) | ❌ pendiente |

---

## 7 · Histórico de sessões

<!-- Formato: "- YYYY-MM-DD — resumo curto do que foi feito e do que ficou pendente". -->

- 2026-09-12 — **Sessão 5 (F3 Skill trees + XP):** completou a F3 que a sessão anterior deixou em RED — `compute_skills`/`tree_for_category`/`TREES` em `app/services/skills.py` (XP derivado, streak por hábito, breakdown, half-up no total), schemas + router `GET /api/skills?end_on=` registrado no `main`, `tests/test_skills_api.py` (5 testes). Suíte **95 passed**, ruff limpo (corrigiu `RUF046` e `RUF034`). Frontend: aba **Habilidades** (`HabilidadesArea.svelte` + CSS) com nível geral, regras de XP e cards por árvore; build sem warnings. E2E vivo estendido para `/api/skills` (+6 checagens na instância isolada, banco vazio → 200, instância real e proxy) — **todas passaram**. Sandbox real: `Estudo Tech` → 420 XP → nível 3 (bate com o sanity check da spec). Pendente: commit+push da F3, proteção de `main`, verificação visual, F4 RAG/Coach IA.

- 2026-09-12 — **Sessão 4 (UI da telemetria rica, em pt-BR):** integrado o frontend que a sessão anterior deixou escrito mas não ligado — shell com abas (`Floresta` / `Árvore` / `Journal`), `ArvoreArea`, `JournalArea`, `MetricsFields`, `NovoHabitPanel`, `RegistrarPanel`, `TreeChart`; `index.html` com `lang="pt-BR"`; restos do starter Svelte removidos. Avisos de a11y do build zerados (hover morto removido dos gráficos, `<label>` que envolvia bloco de texto virou `<div>`). API reiniciada com o código novo (`/tree` saía 404 na instância velha). **Verificação viva** com novo harness `backend/scripts/e2e_verificacao.py`: 30 checagens em HTTP real (banco isolado) + leitura da instância do usuário e do proxy Vite. Achou **1 bug real de UX** (limpar o diário mostrava `Entry removed` como erro) — corrigido. DoD: pytest **65 passed**, ruff limpo, `npm run build` sem warnings. Pendente: proteção de `main`, F3 Skill trees, verificação visual das abas.

- 2026-09-12 — **Sesión 3 (Rediseño UI + F2 Journal):** rediseño completo del frontend con sistema Linear dark (claude-design surface Monitor, anti-slop: 4/10 → 0/10). F2 Journal: modelo `JournalEntry` (1/fecha), router `/api/journal` (PUT upsert con delete-implicito, GET list desc + limit, GET 404), UI panel Journal (textarea markdown mono, mood, tags, entradas recientes). TDD: 4 tests nuevos journal → suite 14; luego 2 más para delete-implicito → suite **16 passed**. Ruff limpio. Verificación viva: container efímero `lifehub-preview` con portas públicas; e2e por proxy (PUT/GET journal OK, entradas recientes visibles no preview). Pendiente: `lifehub-preview` para derribar, proteger `main`, F3 Skill trees.
- 2026-09-12 — **Sesión 2 (Frontend + integración):** commit de la Task C1 interrumpida (proxy Vite + `api.js`); C2 `ForestChart.svelte` (corregido a `$derived` para reactividad sin warnings); C3 `App.svelte` dashboard completo; Parte D: seed demo, smoke e2e real (health, habits, forest, POST sesión vía proxy Vite → Floresta se actualizó de rojo a amarillo en vivo, luego cleanup), README final. Backend 10/10 tests verdes. Todo pusheado a `origin/main`. Pendiente: protección de `main` en GitHub y verificación visual manual.
- 2026-09-11 — **Sesión 1 (Fundación + Backend):** M0 concluido (git init, convenciones, AGENTS, CI, gh auth, repo `ThiagojFalcao/lifehub` creado + push inicial). Parte B backend TDD: models, db, conftest, schemas, routers habits/sessions/forest, `compute_forest`, 10 tests verdes.