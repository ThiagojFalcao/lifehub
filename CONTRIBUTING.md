# Contribuindo para o LifeHub

Projeto solo, mas com disciplina de time. Regras obrigatórias para commits, branches e PRs — "esse projeto não é bagunça".

## Commits (Conventional Commits)

Toda mensagem segue o formato:

```
tipo(escopo): resumo no imperativo (máx ~72 chars)

[corpo opcional: o PORQUÊ da mudança, não "o quê"]
```

| Tipo | Uso |
|---|---|
| `feat` | nova feature / nova capacidade |
| `fix` | correção de bug |
| `refactor` | mudança de código sem alterar comportamento |
| `test` | adição/ajuste de testes |
| `docs` | documentação apenas |
| `chore` | build, deps, config, limpeza |
| `build` | sistema de build/empacotamento |
| `ci` | configurações de CI/CD |

Escopos válidos: `backend`, `frontend`, `api`, `db`, `docs`, `ci`.

Regras:
- **1 commit = 1 mudança lógica.** Nunca "wip", "ajustes", "fix 2".
- Título no **imperativo**, sem ponto final: `feat(backend): endpoint /api/forest`.
- Nada de segredos/chaves em commits (nem em comentários).

## Branches

- `main` é **protegida e sempre deployável**. Só entra via PR mergeado com squash.
- Branches novas a partir do `main`, curtas e descartáveis:
  - `feat/NNN-slug` (ex.: `feat/003-floresta`)
  - `fix/NNN-slug`
  - `chore/NNN-slug`
- Vida útil de horas a dias. Nunca vira branch de longo prazo.

## Pull Requests

- **1 PR = 1 feature/fix.** Ideal < 400 LOC. Se cresceu demais, quebra em PRs menores.
- Preencher o template: o quê, por quê, como testar, critérios de aceite, screenshot (se UI).
- **Merge = squash** → 1 commit limpo no `main`; o título do squash vira o Conventional Commit.
- Antes de abrir/mergear: CI verde (lint + testes + build).

## Ciclo por feature (SDD leve + TDD)

1. **Spec** em `docs/specs/NNN-slug.md` — o quê, por quê, fora de escopo, critérios de aceite.
2. Implementar com **TDD** (lógica): teste falha → implementa → teste verde.
3. Commits frequentes seguindo Conventional Commits.
4. PR pequeno → review → squash-merge.

## Continuidade entre sessões (flight recorder)

O contexto da sessão de chat é **efêmero**. A memória durável do projeto vive no repo.

- Ao fim de **toda sessão de trabalho**, atualizar `PROGRESS.md` **antes** do commit final:
  - `Estado atual` (checkboxes do que ficou pronto),
  - `Próximo passo` (o comando/arquivo exato, sem reler o plano),
  - `Em aberto` (decisões pendentes),
  - linha nova em `Histórico de sessões`.
- Uma sessão nova retoma lendo, **nesta ordem**: `PROGRESS.md` → `AGENTS.md` → `git log`.

## Definição de Pronto (Definition of Done)

Uma feature está pronta quando:

- [ ] Critérios de aceite da spec atendidos.
- [ ] Testes passando (`cd backend && uv run pytest -v`).
- [ ] Lint limpo (`cd backend && uv run ruff check .`).
- [ ] Frontend constrói (`cd frontend && npm run build`).
- [ ] Sem segredos/arquivos de lixo commitados.