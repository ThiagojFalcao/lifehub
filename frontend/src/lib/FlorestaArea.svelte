<script>
  import ForestChart from './ForestChart.svelte'
  import RegistrarPanel from './RegistrarPanel.svelte'
  import NovoHabitPanel from './NovoHabitPanel.svelte'

  /** Área Floresta: visão macro (hábitos distintos/dia) + registro do dia a dia. */
  let { habits = [], forest = [], onsaved } = $props()
</script>

<main class="layout">
  <section class="panel chart-panel">
    <div class="panel-head">
      <h2>Floresta</h2>
      <p>Hábitos distintos completados por dia · linha = média móvel de 7 dias</p>
    </div>
    {#if forest.length}
      <ForestChart days={forest} />
    {:else}
      <div class="empty">
        <p>Sem dados ainda — registre sua primeira sessão.</p>
      </div>
    {/if}
    <div class="legend">
      <span class="legend-item">
        <span class="legend-swatch" style="background:#10b981"></span> no ritmo ou acima
      </span>
      <span class="legend-item">
        <span class="legend-swatch" style="background:#eab308"></span> abaixo do ritmo
      </span>
      <span class="legend-item">
        <span class="legend-swatch" style="background:#e5484d"></span> parado
      </span>
    </div>
  </section>

  <section class="panel form-panel">
    <RegistrarPanel {habits} {onsaved} />
    <NovoHabitPanel {onsaved} />
  </section>
</main>