# PROGRESS.md — LifeHub

> **Flight recorder do projeto.** Atualizado ao fim de **toda sessão de trabalho**.
> Uma sessão nova lê este arquivo + `AGENTS.md` + `git log` e retoma em 30s sem depender da sessão anterior.
>
> Convenção (ver `CONTRIBUTING.md`): ao terminar uma sessão, preencher `Estado atual`, `Próximo passo` e `Em aberto` ANTES do commit final.

---

## Estado atual

**Milestone 0 — Fundação: ✅ CONCLUÍDO.**

- [x] `git init` + `.gitignore` (backend/frontend/db/env)
- [x] `CONTRIBUTING.md` — convenções de commit/PR
- [x] `AGENTS.md` — contexto técnico do projeto
- [x] `docs/specs/000-vertical-slice.md` — spec da 1ª feature
- [x] `.github/workflows/ci.yml` — lint + testes + build em todo PR
- [x] `gh` CLI instalado (v2.100.0) em `~/.local/bin/gh` + PATH no `~/.profile`

**Feature 1 — Vertical slice (tracker + Floresta): ⬜ NÃO INICIADA.**

Plano completo em `.hermes/plans/2026-09-12_000704-lifehub-vertical-slice.md`.
Stack: FastAPI + SQLite (SQLAlchemy 2.0) + Svelte 5 + Vite. TDD: 10 testes backend.

## Próximo passo

1. **Autenticar o `gh`** (precisa do usuário): `gh auth login` → escolher GitHub.com → token/navegador.
2. **Criar repo privado** e fazer o primeiro push.
3. **Começar Feature 1**: implementar o backend TDD (Parte B do plano), task por task.

> Comando de partida da Feature 1 (após montar o scaffold):
> `cd backend && uv sync && uv run pytest -v`  →  esperado `10 passed`.

## Em aberto

- [ ] `gh auth login` (pendente do usuário — token/navegador).
- [ ] Criar repo privado no GitHub (`lifehub`).
- [ ] Definir se Feature 1 roda via subagente ou direto (recomendo subagente).

## Histórico de sessões

<!-- Adicionar uma linha com data + resumo ao fim de cada sessão. -->
- 2026-09-12 — Milestone 0 concluído: fundação (CONVENTION, AGENTS, spec 000, CI) + gh instalado. Feature 1 ainda não iniciada.