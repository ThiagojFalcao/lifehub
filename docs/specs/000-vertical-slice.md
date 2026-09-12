# Spec 000 — Vertical Slice: Tracker + Floresta

Status: aprovada
Depende de: nada (primeira feature)
Fora de escopo: journal, skill trees, XP, RAG/coach, boss battles, export, Docker.

## O quê

Primeiro incremento de ponta a ponta do LifeHub: registrar hábitos e sessões (dados
ricos, não binários) e visualizar a "Floresta" (barras diárias + linha de tendência
7 dias + cores), rodando local-first.

## Por quê

Valida a arquitetura (backend FastAPI + SQLite + frontend Svelte) com um caminho de
valor curto e shippável, antes dos sistemas complexos (IA, skill trees) que virão.

## Glossário

- **Hábito (Habit):** entidade rastreada (ex. "Estudo Tech", "Corrida"). Carrega
  `metrics_schema` (JSON) declarando quais métricas rastreia — não é binário.
- **Sessão (Session):** ocorrência de um hábito num dia, com `duration_min`,
  `metrics` (JSON rico por hábito), `floor_plan_used`.
- **Floresta (Forest):** gráfico semanal. Barra = hábitos **distintos** completados
  no dia; linha = média móvel 7 dias; cores verde (≥ média), amarela (>0 e < média),
  vermelha (0).

## Critérios de aceite

1. `POST/GET /api/habits` e `GET /api/habits/{id}` criam/listam hábitos com
   `metrics_schema` JSON.
2. `POST/GET /api/sessions` registram/listam sessões; exige hábito válido (404) e
   `duration_min > 0` (422).
3. `GET /api/forest?days=7&end_on=YYYY-MM-DD` conta hábitos **distintos** por dia,
   calcula média móvel 7d e cores.
4. Dashboard Svelte renderiza a Floresta e permite registrar sessão + criar hábito.
5. Suíte backend verde (10 testes).

## API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/health` | healthcheck |
| POST/GET | `/api/habits` | criar/listar hábitos |
| GET | `/api/habits/{id}` | detalhe do hábito |
| POST/GET | `/api/sessions?habit_id=` | registrar/listar sessões |
| GET | `/api/forest?days=&end_on=` | agregação da Floresta |

## Decisões

- Modelo "rico" via coluna `JSON` (tradeoff flexibilidade × validação forte) — registrado
  em `docs/adr/` quando criado.
- Agregação da Floresta é função pura (`app/services/forest.py`), testável isolada.

## Implementação

Ver `.hermes/plans/2026-09-12_000704-lifehub-vertical-slice.md` (passo a passo com código).