<script>
  import { api } from './api.js'
  import MetricsFields from './MetricsFields.svelte'
  import { cleanValues, emptyValues, hoje } from './metrics.js'

  /** Registrar sessão: uma ocorrência de um hábito, com as métricas ricas dele. */
  let { habits = [], onsaved } = $props()

  let form = $state({
    habit_id: '',
    date: hoje(),
    duration_min: 30,
    notes: '',
    floor_plan_used: false,
    metrics: {},
  })
  let message = $state('')
  let error = $state('')
  let enviando = $state(false)

  let habitAtual = $derived(habits.find((h) => String(h.id) === String(form.habit_id)) ?? null)

  // Autosseleciona o primeiro hábito quando a lista chega.
  $effect(() => {
    if (!form.habit_id && habits.length) form.habit_id = String(habits[0].id)
  })

  // Reseta as métricas só quando o hábito MUDA — assim um reload da lista (após
  // salvar) não apaga o que o usuário acabou de digitar.
  let schemaAplicado = null
  $effect(() => {
    const id = form.habit_id
    if (id === schemaAplicado) return
    schemaAplicado = id
    form.metrics = emptyValues(habitAtual?.metrics_schema)
  })

  async function registrar(e) {
    e.preventDefault()
    error = ''
    message = ''
    if (!form.habit_id) {
      error = 'Escolha um hábito.'
      return
    }
    enviando = true
    try {
      await api('/api/sessions', {
        method: 'POST',
        body: {
          habit_id: Number(form.habit_id),
          date: form.date,
          duration_min: Number(form.duration_min),
          notes: form.notes.trim() || null,
          metrics: cleanValues(form.metrics),
          floor_plan_used: form.floor_plan_used,
        },
      })
      form.notes = ''
      form.floor_plan_used = false
      form.metrics = emptyValues(habitAtual?.metrics_schema)
      message = 'Sessão registrada'
      setTimeout(() => (message = ''), 2500)
      onsaved?.()
    } catch (err) {
      error = String(err?.message ?? err)
    } finally {
      enviando = false
    }
  }
</script>

<div class="panel-head">
  <h2>Registrar sessão</h2>
  <p>Uma ocorrência de um hábito, com os dados que aquele hábito declara</p>
</div>

<form onsubmit={registrar}>
  <label class="field">
    <span>Hábito</span>
    <select bind:value={form.habit_id}>
      {#each habits as h (h.id)}<option value={h.id}>{h.name}</option>{/each}
    </select>
  </label>

  {#if habitAtual?.floor_plan}
    <div class="field">
      <span>Floor plan</span>
      <p class="floor-plan">{habitAtual.floor_plan}</p>
    </div>
    <label class="field">
      <span class="check-row">
        <input type="checkbox" bind:checked={form.floor_plan_used} />
        <span>Usei o floor plan</span>
      </span>
    </label>
  {/if}

  <label class="field">
    <span>Data</span>
    <input type="date" bind:value={form.date} />
  </label>

  <label class="field">
    <span>Duração (min)</span>
    <input type="number" min="1" bind:value={form.duration_min} />
  </label>

  <MetricsFields schema={habitAtual?.metrics_schema} bind:values={form.metrics} />

  <label class="field">
    <span>Notas</span>
    <input type="text" bind:value={form.notes} placeholder="opcional" />
  </label>

  <button type="submit" class="primary" disabled={enviando}>
    {enviando ? 'Registrando…' : 'Registrar'}
  </button>
  {#if message}<p class="ok">{message}</p>{/if}
  {#if error}<p class="err">{error}</p>{/if}
</form>