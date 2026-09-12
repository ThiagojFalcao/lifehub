<script>
  import { onMount } from 'svelte'
  import ForestChart from './lib/ForestChart.svelte'
  import { api } from './lib/api.js'

  let habits = $state([])
  let forest = $state([])
  let error = $state('')
  let message = $state('')
  let habitName = $state('')

  let form = $state({
    habit_id: '',
    date: new Date().toISOString().slice(0, 10),
    duration_min: 30,
    notes: '',
  })

  async function load() {
    try {
      const [h, f] = await Promise.all([
        api('/api/habits'),
        api('/api/forest?days=14'),
      ])
      habits = h
      forest = f.days
      if (!form.habit_id && h.length) form.habit_id = String(h[0].id)
    } catch (e) {
      error = String(e)
    }
  }

  async function addHabit(e) {
    e.preventDefault()
    try {
      await api('/api/habits', {
        method: 'POST',
        body: { name: habitName, category: 'study_tech', metrics_schema: {}, floor_plan: '' },
      })
      habitName = ''
      await load()
    } catch (err) {
      error = String(err)
    }
  }

  async function logSession(e) {
    e.preventDefault()
    try {
      await api('/api/sessions', {
        method: 'POST',
        body: {
          habit_id: Number(form.habit_id),
          date: form.date,
          duration_min: Number(form.duration_min),
          notes: form.notes.trim() || null,
          metrics: {},
          floor_plan_used: Number(form.duration_min) < 15,
        },
      })
      form = { ...form, notes: '' }
      message = 'Sessão registrada ✓'
      await load()
    } catch (err) {
      error = String(err)
    }
  }

  onMount(load)
</script>

<header>
  <h1>🌲 LifeHub</h1>
  <p>Floresta — hábitos completados por dia</p>
</header>

<div class="grid">
  <section class="card">
    <h2>Registrar sessão</h2>
    <form onsubmit={logSession}>
      <label>
        Hábito
        <select bind:value={form.habit_id}>
          {#each habits as h}<option value={h.id}>{h.name}</option>{/each}
        </select>
      </label>
      <label>Data <input type="date" bind:value={form.date} /></label>
      <label>Duração (min) <input type="number" min="1" bind:value={form.duration_min} /></label>
      <label>Notas <input type="text" bind:value={form.notes} /></label>
      <button type="submit">Registrar</button>
    </form>
    {#if message}<p class="ok">{message}</p>{/if}
  </section>

  <section class="card">
    <h2>Novo hábito</h2>
    <form onsubmit={addHabit}>
      <input type="text" bind:value={habitName} placeholder="Nome do hábito" />
      <button type="submit">Criar</button>
    </form>
  </section>
</div>

<section class="card">
  {#if forest.length}
    <ForestChart days={forest} />
  {:else}
    <p>Sem dados ainda — registre sua primeira sessão.</p>
  {/if}
</section>

{#if error}<p class="err">{error}</p>{/if}

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
  }
  header { padding: 1.5rem; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding: 0 1.5rem; }
  .card { background: #1e293b; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
  form { display: flex; flex-direction: column; gap: 0.5rem; }
  label { display: flex; flex-direction: column; font-size: 0.85rem; gap: 0.25rem; }
  input, select, button { padding: 0.4rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
  button { cursor: pointer; background: #3b82f6; border: none; color: white; }
  .ok { color: #22c55e; }
  .err { color: #ef4444; }
</style>