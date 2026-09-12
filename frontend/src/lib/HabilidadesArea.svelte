<script>
  import { onMount } from 'svelte'
  import { api } from './api.js'

  /** Área Habilidades: XP derivado das sessões, por árvore (Spec 002). */
  let skills = $state(null)
  let carregando = $state(false)
  let error = $state('')

  async function carregar() {
    carregando = true
    try {
      skills = await api('/api/skills')
      error = ''
    } catch (e) {
      error = String(e?.message ?? e)
    } finally {
      carregando = false
    }
  }

  onMount(carregar)

  function pct(valor) {
    return Math.round((valor ?? 0) * 100)
  }
</script>

<main class="layout">
  <section class="panel">
    <div class="panel-head">
      <h2>Nível geral</h2>
      <p>XP acumulado de todas as árvores — cada sessão registrada vira XP</p>
    </div>

    {#if error}
      <p class="err">{error}</p>
    {:else if carregando}
      <p class="hint">carregando…</p>
    {:else if skills}
      <div class="stat-grid">
        <div class="stat">
          <span class="stat-value">{skills.level}</span>
          <span class="stat-label">nível geral</span>
        </div>
        <div class="stat">
          <span class="stat-value">{skills.total_xp}<small>xp</small></span>
          <span class="stat-label">pontos totais</span>
        </div>
      </div>

      <div class="level-bar" aria-hidden="true">
        <div class="level-bar-fill" style="width: {pct(skills.progresso)}%"></div>
      </div>
      <p class="hint">
        {skills.xp_no_nivel} / {skills.xp_para_proximo} XP para o nível {skills.level + 1}
        ({pct(skills.progresso)}%)
      </p>
    {:else}
      <p class="hint">Nenhum dado ainda.</p>
    {/if}
  </section>

  <section class="panel form-panel">
    <div class="panel-head">
      <h2>Como o XP funciona</h2>
      <p>XP é derivado, não digitado</p>
    </div>
    <ul class="xp-rules">
      <li><b>Base</b> — 1 XP por minuto de sessão</li>
      <li><b>Floor plan</b> — +25% quando você usa o plano mínimo</li>
      <li><b>Telemetria</b> — +10 XP por sessão com métricas preenchidas</li>
      <li><b>Constância</b> — +2 XP por dia de sequência (até 5 dias)</li>
    </ul>
  </section>
</main>

<section class="wide-panel panel">
  <div class="panel-head">
    <h2>Árvores de habilidade</h2>
    <p>Cada árvore agrupa hábitos da mesma natureza</p>
  </div>

  {#if skills?.trees?.length}
    <div class="tree-grid">
      {#each skills.trees as tree (tree.id)}
        <article class="tree-card">
          <div class="tree-card-head">
            <h3>{tree.name}</h3>
            <span class="tree-level">nvl {tree.level}</span>
          </div>

          <div class="level-bar" aria-hidden="true">
            <div class="level-bar-fill" style="width: {pct(tree.progresso)}%"></div>
          </div>
          <p class="hint">
            {tree.xp_no_nivel} / {tree.xp_para_proximo} XP · {pct(tree.progresso)}%
          </p>

          <div class="breakdown">
            {#each Object.entries(tree.breakdown) as [fonte, valor] (fonte)}
              <span class="chip">
                <b>{fonte}</b>
                {valor}
              </span>
            {/each}
          </div>

          {#if tree.habits.length}
            <ul class="tree-habits">
              {#each tree.habits as h (h.id)}
                <li>
                  <span class="tree-habit-name">{h.name}</span>
                  <span class="tree-habit-xp">{h.xp} XP</span>
                </li>
              {/each}
            </ul>
          {:else}
            <p class="hint">Nenhum hábito ainda — crie um e registre sessões.</p>
          {/if}
        </article>
      {/each}
    </div>
  {:else}
    <p class="hint">Sem dados de habilidades ainda.</p>
  {/if}
</section>