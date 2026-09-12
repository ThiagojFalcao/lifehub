<script>
  import { api } from './api.js'
  import TreeChart from './TreeChart.svelte'
  import { formatMetric } from './metrics.js'

  /** Área Árvore: histórico de UM hábito — intensidade por dia, totais e Galhos. */
  let { habits = [] } = $props()

  let habitId = $state('')
  let dias = $state(30)
  let tree = $state(null)
  let galhos = $state([])
  let carregando = $state(false)
  let error = $state('')

  let habitAtual = $derived(habits.find((h) => String(h.id) === String(habitId)) ?? null)
  let summary = $derived(tree?.summary ?? null)

  // Autosseleciona o primeiro hábito quando a lista chega.
  $effect(() => {
    if (!habitId && habits.length) habitId = String(habits[0].id)
  })

  // Recarrega quando o hábito ou a janela de dias mudam.
  $effect(() => {
    const id = habitId
    const janela = Number(dias)
    if (!id) return
    carregar(id, janela)
  })

  async function carregar(id, janela) {
    carregando = true
    try {
      const [t, s] = await Promise.all([
        api(`/api/habits/${id}/tree?days=${janela}`),
        api(`/api/sessions?habit_id=${id}`),
      ])
      tree = t
      galhos = s
      error = ''
    } catch (e) {
      error = String(e?.message ?? e)
    } finally {
      carregando = false
    }
  }
</script>

<main class="layout">
  <section class="panel">
    <div class="panel-head">
      <h2>Árvore {#if habitAtual}— {habitAtual.name}{/if}</h2>
      <p>Minutos investidos por dia neste hábito · linha = média móvel de 7 dias</p>
    </div>

    <div class="toolbar">
      <label class="field">
        <span>Hábito</span>
        <select bind:value={habitId}>
          {#each habits as h (h.id)}<option value={h.id}>{h.name}</option>{/each}
        </select>
      </label>
      <label class="field">
        <span>Janela</span>
        <select bind:value={dias}>
          <option value={14}>14 dias</option>
          <option value={30}>30 dias</option>
          <option value={90}>90 dias</option>
          <option value={365}>1 ano</option>
        </select>
      </label>
      <span class="spacer"></span>
      {#if carregando}<span class="status-text">carregando…</span>{/if}
    </div>

    {#if habitAtual?.floor_plan}
      <p class="floor-plan">{habitAtual.floor_plan}</p>
    {/if}

    {#if error}
      <p class="err">{error}</p>
    {:else if !habits.length}
      <div class="empty"><p>Crie um hábito na área Floresta para ver a Árvore.</p></div>
    {:else if tree?.days?.length}
      <TreeChart days={tree.days} />
    {:else}
      <div class="empty"><p>Sem sessões registradas para este hábito.</p></div>
    {/if}
  </section>

  <section class="panel form-panel">
    <div class="panel-head">
      <h2>Progresso cumulativo</h2>
      <p>Todo o histórico, não só a janela</p>
    </div>

    {#if summary}
      <div class="stat-grid">
        <div class="stat">
          <span class="stat-value">{summary.total_hours}<small>h</small></span>
          <span class="stat-label">tempo total</span>
        </div>
        <div class="stat">
          <span class="stat-value">{summary.total_sessions}</span>
          <span class="stat-label">sessões</span>
        </div>
        <div class="stat">
          <span class="stat-value">{summary.active_days}</span>
          <span class="stat-label">dias ativos</span>
        </div>
        <div class="stat">
          <span class="stat-value">{summary.current_streak}</span>
          <span class="stat-label">sequência atual</span>
        </div>
        <div class="stat">
          <span class="stat-value">{summary.best_streak}</span>
          <span class="stat-label">melhor sequência</span>
        </div>
        <div class="stat">
          <span class="stat-value">{summary.avg_min_per_active_day}<small>min</small></span>
          <span class="stat-label">média por dia ativo</span>
        </div>
      </div>
    {:else}
      <p class="hint">Escolha um hábito para ver os totais.</p>
    {/if}
  </section>
</main>

<section class="wide-panel panel">
  <div class="panel-head">
    <h2>Galhos</h2>
    <p>Cada sessão registrada, com as métricas que o hábito declara</p>
  </div>

  {#if galhos.length}
    <ul class="branch-list">
      {#each galhos as s (s.id)}
        <li class="branch">
          <div class="branch-head">
            <span class="branch-date">{s.date}</span>
            <span class="branch-dur">{s.duration_min} min</span>
            {#if s.floor_plan_used}<span class="badge">floor plan</span>{/if}
          </div>
          {#if Object.keys(s.metrics || {}).length}
            <div class="metric-chips">
              {#each Object.entries(s.metrics) as [nome, valor] (nome)}
                <span class="chip"><b>{nome}</b>{formatMetric(valor)}</span>
              {/each}
            </div>
          {/if}
          {#if s.notes}<p class="branch-notes">{s.notes}</p>{/if}
        </li>
      {/each}
    </ul>
  {:else}
    <p class="hint">Nenhuma sessão registrada neste hábito ainda.</p>
  {/if}
</section>
