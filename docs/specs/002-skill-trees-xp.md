# Spec 002 — Skill trees + XP

Status: **aprovada** (2026-09-12 — decisões 1, 2, 3 e 4 aprovadas exatamente como propostas)
Depende de: Spec 001 (telemetria rica + Árvore + Galhos)
Fora de escopo: boss battles, RAG/coach, notificações, gráfico de XP por dia, nós/perks
desbloqueáveis, XP manual ou ajustável, import/export, Docker, git auto-sync.

## O quê

Camada de **progressão**: cada sessão registrada vira XP, XP vira **nível**, e os níveis
agregam-se em **árvores de habilidade** (Tech · Exercício · Hidratação · Geral). Reaproveita
as sessões e o `metrics_schema` que já existem — **sem tabela nova e sem migração**.

## Por quê

O roadmap promete "skill trees + XP" desde o M0, e o app hoje só mostra **estado**
(Floresta = constância, Árvore = intensidade, Journal = narrativa). Nada **acumula**.
Sem isso o LifeHub mede mas não recompensa, e a telemetria rica destravada pela F2.5
(`metrics_schema`, `floor_plan_used`) não tem consequência nenhuma dentro do produto.

## Glossário

- **Árvore de habilidade (skill tree):** agrupamento de hábitos de mesma natureza
  (ex.: `study_tech` → Tech). Tem XP e nível próprios.
- **XP:** pontos derivados das sessões já registradas — não é um contador digitado.
- **Nível:** faixa de XP acumulado, pela curva triangular da Decisão 3.
- **Breakdown:** de onde o XP veio (`base`, `floor_plan`, `metrics`, `streak`). Nível
  sem explicação não é telemetria.

## Decisões

### 1. XP é **derivado**, não armazenado

`compute_skills(...)` é função pura em `app/services/skills.py`, sobre as sessões já
persistidas — mesmo padrão de `compute_forest`/`compute_tree`. **Nenhuma coluna `xp`.**

Trade-offs (o porquê de derivar em vez de somar num campo):

| | Derivado (escolhido) | Coluna persistida |
|---|---|---|
| Drift sessão × XP | impossível (fonte única) | possível (dois writes) |
| Dados históricos | ganham XP retroativo de graça | precisariam de backfill |
| Mudar a fórmula | recalcula o passado | script de correção |
| Custo | O(n sessões) a cada GET | O(1) leitura |
| Bônus ad-hoc / ajuste manual | não dá | dá |

Custo irrelevante em SQLite local com milhares de linhas; os dois "contra" estão fora de
escopo. Migrar para persistido depois é possível sem perder nada (o derivado é a verdade).

### 2. Fórmula (constantes nomeadas no topo do módulo, tunáveis)

| Componente | Regra |
|---|---|
| Base | **1 XP por minuto** → `duration_min` |
| Floor plan | **×1.25** quando `floor_plan_used` (recompensa o comportamento anti-motivação) |
| Telemetria rica | **+10 XP** quando a sessão tem `metrics` não vazio |
| Constância | **+2 XP × min(streak_do_dia − 1, 5)** → de 0 a +10 XP |

Soma arredondada para inteiro (half-up) uma única vez, no fim.

### 3. Curva de nível: triangular

Nível **N** começa em `50 · N · (N−1)` XP acumulado:

| Nível | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| XP acumulado | 0 | 100 | 300 | 600 | 1000 | 1500 |

"Cada nível pede 100 XP mais que o anterior" — legível, monotônica, e sem exponencial que
estoura para quem registra 4h de estudo. Sanidade com o seed atual (`study_tech`: 7 sessões
de 50 min em 14 dias): ~420 XP → **nível 3**.

### 4. Categoria → árvore, com registro explícito e fallback

| `habit.category` | árvore |
|---|---|
| `study_tech` | Tech |
| `running`, `exercise`, `gym`, `workout` | Exercício |
| `water`, `hydration` | Hidratação |
| **qualquer outra** (ex.: `reading`) | **Geral** |

`category` é string livre hoje; o fallback **Geral** evita quebrar `POST /api/habits` e
absorve hábitos novos sem deploy. Alternativa considerada: 4ª árvore fixa "Leitura" e
`reading` mapeada nela — mais bonito no seed, mais um caso especial para manter.

### 5. Transparência obrigatória

A resposta traz `breakdown` por árvore (e o total). O usuário vê **por que** está no
nível 3, não só que está.

### 6. Sem nós/perks na v1

Árvore = nível + barra de progresso + hábitos que a alimentam. Nós desbloqueáveis são
renda de outra feature (YAGNI).

## Critérios de aceite

1. `GET /api/skills?end_on=YYYY-MM-DD` devolve:
   - `trees[]` com `id`, `name`, `xp`, `level`, `xp_no_nivel`, `xp_para_proximo`,
     `progresso` (0..1), `breakdown`, `habits[]` (`id`, `name`, `xp`, `level`);
   - `total_xp`, `level` (nível geral, mesma curva), `xp_no_nivel`, `xp_para_proximo`,
     `progresso`;
   - **árvores vazias também aparecem** (xp 0, nível 1) — a UI mostra o que ainda não
     foi regado.
2. XP do hábito = soma do XP das suas sessões; XP da árvore = soma dos seus hábitos.
3. Limites de nível fechados e testados: 0 → 1 · 99 → 1 · 100 → 2 · 299 → 2 · 300 → 3 ·
   600 → 4 · 1000 → 5.
4. `progresso` bem definido para qualquer `xp ≥ 0`, arredondado com 2 casas.
5. Sessão com `duration_min` alto e `metrics` vazio pontua normal; `metrics` só com chaves
   não-numéricas também (o bônus é pela **presença** de telemetria, não pelo tipo).
6. Banco vazio ou hábito sem sessão → `total_xp = 0`, árvores nível 1, **HTTP 200**
   (não 500, não lista vazia).
7. `end_on` aceita data passada e limita o cálculo (XP "até aquela data") — permite ao
   frontend mostrar progresso histórico.
8. Suíte verde (65 atuais + novos), `ruff check` limpo, `npm run build` sem warnings.
9. Nova área **Habilidades** na navegação (Floresta · Árvore · Journal · Habilidades),
   em pt-BR, reaproveitando o CSS existente (`.stat-grid`, `.chip`).
10. Verificação viva: `backend/scripts/e2e_verificacao.py` passa a cobrir `/api/skills`
    (incluindo o caso de banco vazio → 200).

## API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/skills?end_on=YYYY-MM-DD` | árvores + níveis + breakdown + total geral |

Nenhuma rota de escrita: XP não se escreve, se registra sessão.

## Riscos

- **Fórmula tunável = números que já foram vistos podem mudar** quando a constante mudar.
  Mitigação: constantes nomeadas no topo do módulo + tabela desta spec como contrato.
- **Streak por sessão** precisa do histórico do hábito inteiro (não só a janela):
  uma passada ordenada sobre as datas, O(n log n) — nunca quadrático.
- **`reading` cai em Geral** e pode surpreender quem esperava ver "Leitura" na UI.
  Decisão consciente (fallback), revisável se o usuário criar uma 4ª árvore.

## Implementação

TDD, tarefa a tarefa (ver `.hermes/plans/` — plano não versionado, gerado após a
aprovação desta spec).
