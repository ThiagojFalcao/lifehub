# Spec 001 — Telemetria rica + Árvore + Galhos

Status: aprovada
Depende de: Spec 000 (vertical slice)
Fora de escopo: skill trees/XP, boss battles, RAG/coach, export, Docker, git auto-sync.

## O quê

Fechar a promessa central do LifeHub: **rastreio rico e não-binário** de hábitos, com a
visualização multi-nível **Floresta → Árvore → Galhos** completa. Ao fim deste incremento
o app deixa de ser "CRUD + um gráfico" e passa a ser o sistema de telemetria descrito na
especificação do projeto.

## Por quê

Hoje o modelo declara `metrics_schema` por hábito (`{"focus_minutes": "int", ...}`) mas a
UI **nunca** pede essas métricas — o formulário de sessão envia `metrics: {}` fixo e o de
hábito cria com `category: "study_tech"` e `metrics_schema: {}` chumbados no código. O banco
promete "rich, not binary"; a aplicação entrega binário. E das três visualizações exigidas
pelo MVP, só a Floresta existe: **Árvore** (histórico de um hábito) e **Galhos** (detalhe
das sessões) não existem.

## Glossário

- **Árvore (Tree):** histórico de **um** hábito ao longo do tempo. Uma barra por dia com a
  duração total, linha de tendência (média móvel 7d da duração) e cores. Distinta da
  Floresta, que conta hábitos **distintos** por dia.
- **Galhos (Branches):** as sessões individuais de um hábito — os dados ricos por sessão
  (`metrics`), duração, `floor_plan_used`, notas.
- **Métrica declarada:** chave presente no `metrics_schema` do hábito.
- **Métrica livre:** chave enviada em `metrics` que o hábito não declarou.

## Critérios de aceite

1. `POST /api/sessions` **valida** `metrics` contra o `metrics_schema` do hábito:
   - tipo compatível com o declarado → aceita (com coerção — ver Decisões);
   - tipo incompatível com o declarado → **422**;
   - métrica livre (não declarada) → aceita (schema evolutivo);
   - hábito sem `metrics_schema` → aceita qualquer coisa.
2. `GET /api/habits/{id}/tree?days=N&end_on=YYYY-MM-DD` devolve:
   - `habit`: o hábito;
   - `days[]`: um item por dia (`date`, `sessions`, `duration_min`, `avg_7d_min`, `color`);
   - `summary`: `total_sessions`, `total_min`, `total_hours`, `active_days`,
     `current_streak`, `best_streak`, `avg_min_per_active_day`.
   - 404 se o hábito não existir.
3. `GET /api/sessions?habit_id=` ordena de forma **determinística**: `date desc, id desc`.
4. Dashboard com **navegação por áreas** (Floresta · Árvore · Journal) preservando o
   sistema visual Linear dark já aprovado.
5. Área Floresta: registrar sessão com **campos de métrica gerados dinamicamente** a partir
   do `metrics_schema` do hábito selecionado + `floor_plan` visível com botão "usei o floor plan".
6. Criar hábito com **categoria escolhível** (não chumbada), floor plan e **editor de
   metrics_schema** (linhas nome + tipo).
7. Área Árvore: seletor de hábito, `TreeChart` (barras + tendência + cores), painel de
   **progresso cumulativo** e lista de **Galhos** (sessões) com as métricas renderizadas.
8. Suíte backend verde (16 testes atuais + novos), `ruff check` limpo, `npm run build` sem erro.
9. UI e docs do repo em **pt-BR**.

## API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/habits/{id}/tree?days=&end_on=` | Árvore: histórico do hábito + summary |
| GET | `/api/sessions?habit_id=` | Galhos (já existia; passa a ordenar por `date desc, id desc`) |
| POST | `/api/sessions` | passa a validar `metrics` contra o `metrics_schema` |

## Decisões

- **`metrics_schema` é dica, não jaula.** O schema evolutivo é requisito explícito do
  projeto ("não travar estrutura inicial"). Por isso métrica livre passa e só o tipo
  **declarado e violado** gera 422. Validar presença de todas as chaves declaradas
  quebraria a retrocompatibilidade com o seed e com dados históricos.
- **Coerção tolerante** em `app/services/metrics.py`: HTML `<input>` entrega `str`, então
  `"60"` → `60` para `int`/`float` e `"true"` → `True` para `bool`; `60.0` → `60` para `int`
  quando o valor é inteiro. Justificativa: a fronteira HTTP não deve obrigar a UI a
  pré-tipar, e o dado persistido nasce correto.
- **A Árvore mede duração, a Floresta mede amplitude.** A Floresta conta hábitos distintos
  por dia (amplitude da vida); a Árvore mostra a intensidade de um hábito (duração). Reusar
  a mesma métrica nas duas telas tornaria a Árvore uma Floresta filtrada, sem valor.
- **Galhos reusa `GET /api/sessions?habit_id=`.** Nenhum endpoint novo — o recurso já
  existe e devolve a sessão completa com `metrics`. YAGNI.
- **Lógica de agregação continua em funções puras** (`app/services/`), testáveis isoladas.
- **Áreas em abas numa única página**, sem roteador: a decisão foi evoluir a base atual, e
  um roteador não paga o custo agora.

## Implementação

Ver `.hermes/plans/2026-09-12_153008-lifehub-telemetria-rica.md`.
