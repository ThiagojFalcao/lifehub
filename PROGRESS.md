# PROGRESS.md — LifeHub

> **Flight recorder do projeto.** Este arquivo é a fonte de verdade do "onde estamos".
> Atualizado ao fim de **toda sessão de trabalho** — e reaberto em **toda sessão nova**.
>
> **Ordem de leitura numa sessão nova:** `PROGRESS.md` → `AGENTS.md` → `git log --oneline -20`.
> Regra de atualização em `CONTRIBUTING.md`.

---

## 1 · Visão geral

**LifeHub** — sistema local-first de telemetria pessoal e progressão de habilidades:
tracker de hábitos não-binários, visualização "Floresta", skill trees, XP, journal e coach IA.
Construção **incremental, feature por feature**, com TDD e CI desde o início.

**Stack:** Python 3.13 · FastAPI · SQLAlchemy 2.0 · SQLite · Svelte 5 · Vite · GitHub Actions.
**Repo:** privado no GitHub (`ThiagojFalcao`) — ainda a ser criado.

---

## 2 · Roadmap (milestones / features)

| # | Feature | Spec | Status |
|---|---------|------|--------|
| M0 | Fundação: git init, `.gitignore`, convenções, AGENTS, CI | — | ✅ concluído |
| F1 | Vertical slice: tracker de hábitos + visualização Floresta | `docs/specs/000-vertical-slice.md` | ⬜ não iniciado |
| F2 | Journal + nota diária (híbrido) | `docs/specs/00X-journal.md` | ⬛ backlog |
| F3 | Skill trees (Tech / Exercício / Hidratação) + XP | — | ⬛ backlog |
| F4 | RAG / Coach IA | — | ⬛ backlog |
| F5 | Boss Battles | — | ⬛ backlog |
| F6 | git auto-sync + Docker (portabilidade) | — | ⬛ backlog |

> ⬜ = próximo / em andamento · ⬛ = backlog (goal do usuário: subir feature por feature no GitHub).

---

## 3 · Estado atual

**Milestone 0 — Fundação: ✅ CONCLUÍDO.**

- [x] `git init` + `.gitignore` (backend/frontend/db/env)
- [x] `CONTRIBUTING.md` — convenções de commit/PR + flight recorder
- [x] `AGENTS.md` — contexto técnico + "como retomar"
- [x] `README.md`
- [x] `docs/specs/000-vertical-slice.md` — spec da F1
- [x] `.github/workflows/ci.yml` — ruff + pytest + build em todo PR
- [x] Identidade git: `Thiago Falcão <167378662+ThiagojFalcao@users.noreply.github.com>`
- [x] `gh` CLI instalado (v2.100.0) em `~/.local/bin/gh` + PATH no `~/.profile`

**Feature 1 — Vertical slice (tracker + Floresta): ⬜ NÃO INICIADA.**

Plano passo a passo em `.hermes/plans/2026-09-12_000704-lifehub-vertical-slice.md`.
Alvo: FastAPI + SQLite + Svelte 5, TDD com **10 testes backend** passando.

---

## 4 · Próximo passo

1. **Autenticar `gh`** (precisa do usuário — ver seção 6):
   `gh auth login` → GitHub.com → HTTPS → *Login with a web browser* (gera código 8-dígitos).
2. **Criar repo privado + push inicial** (ver seção 6).
3. **Feature 1**: montar scaffold (Parte A do plano), depois backend TDD (Parte B).

> Comando de partida da F1 (após scaffold):
> `cd backend && uv sync && uv run pytest -v` → esperado `10 passed`.

---

## 5 · Em aberto (decisões pendentes)

- [ ] Autenticar `gh` (pendente de interação do usuário).
- [ ] Criar repo privado no GitHub (nome sugerido: `lifehub`).
- [ ] Feature 1: implementar via subagente ou direto (recomendo subagente).
- [ ] Push inicial: com os 5 commits atuais da M0.

---

## 6 · Conectar ao GitHub (checklist)

| Passo | Comando / ação | Estado |
|-------|----------------|--------|
| 1. Autenticar `gh` | `gh auth login` (browser → colar código) | ❌ pendente |
| 2. Criar repo privado | `gh repo create lifehub --private --source=. --remote=origin --push` | ❌ pendente |
| 3. Push inicial | (coberto pelo `--push` acima) | ❌ pendente |
| 4. Proteger `main` | GitHub → Settings → Branches → proteção (só via PR) | ❌ pendente |

---

## 7 · Histórico de sessões

<!-- Formato: "- YYYY-MM-DD — resumo curto do que foi feito e do que ficou pendente". -->

- 2026-09-12 — M0 concluído (fundação + gh instalado). Criado `PROGRESS.md` como flight recorder. Pendente: autenticar `gh` e criar repo.