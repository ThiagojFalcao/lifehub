<script>
  import { onMount } from 'svelte'
  import ForestChart from './lib/ForestChart.svelte'
  import { api } from './lib/api.js'

  let habits = $state([])
  let forest = $state([])
  let error = $state('')
  let message = $state('')
  let habitName = $state('')

  let entries = $state([])
  let journal = $state({
    date: new Date().toISOString().slice(0, 10),
    content: '',
    mood: '',
    tags: '',
  })
  let journalMsg = $state('')

  let form = $state({
    habit_id: '',
    date: new Date().toISOString().slice(0, 10),
    duration_min: 30,
    notes: '',
  })

  let showAddHabit = $state(false)

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

  async function loadJournal() {
    try {
      entries = await api('/api/journal?limit=14')
    } catch (e) {
      error = String(e)
    }
  }

  async function saveJournal(e) {
    e.preventDefault()
    try {
      const tags = journal.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
      await api(`/api/journal/${journal.date}`, {
        method: 'PUT',
        body: {
          content: journal.content,
          mood: journal.mood || null,
          tags,
        },
      })
      journalMsg = 'Diário guardado'
      setTimeout(() => (journalMsg = ''), 2500)
      await loadJournal()
    } catch (err) {
      error = String(err)
    }
  }

  async function editEntry(d) {
    try {
      const entry = await api(`/api/journal/${d}`)
      journal = {
        date: d,
        content: entry.content,
        mood: entry.mood || '',
        tags: (entry.tags || []).join(', '),
      }
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
      showAddHabit = false
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
      message = 'Sessão registrada'
      await load()
      setTimeout(() => (message = ''), 2500)
    } catch (err) {
      error = String(err)
    }
  }

  onMount(() => {
    load()
    loadJournal()
  })
</script>

<header>
  <div class="brand">
    <span class="dot" aria-hidden="true"></span>
    <div>
      <h1>LifeHub</h1>
      <p class="sub">Telemetria personal · local-first</p>
    </div>
  </div>
  <div class="status">
    <span class="live-dot" aria-hidden="true"></span>
    <span class="status-text">local</span>
    {#if forest.length}
      <span class="pill">últimos {forest.length} d</span>
    {/if}
  </div>
</header>

<main>
  <section class="panel chart-panel">
    <div class="panel-head">
      <h2>Floresta</h2>
      <p>Hábitos distintos completados por dia · média móvil 7d</p>
    </div>
    {#if forest.length}
      <ForestChart days={forest} />
    {:else}
      <div class="empty">
        <p>Sem dados ainda — registre sua primeira sessão.</p>
      </div>
    {/if}
  </section>

  <section class="panel form-panel">
    <div class="panel-head">
      <h2>Registrar sessão</h2>
      <p>Una ocurrencia de un hábito, con datos ricos</p>
    </div>
    <form onsubmit={logSession}>
      <label class="field">
        <span>Hábito</span>
        <select bind:value={form.habit_id}>
          {#each habits as h}<option value={h.id}>{h.name}</option>{/each}
        </select>
      </label>
      <label class="field">
        <span>Data</span>
        <input type="date" bind:value={form.date} />
      </label>
      <label class="field">
        <span>Duración (min)</span>
        <input type="number" min="1" bind:value={form.duration_min} />
      </label>
      <label class="field">
        <span>Notas</span>
        <input type="text" bind:value={form.notes} placeholder="opcional" />
      </label>
      <button type="submit" class="primary">Registrar</button>
      {#if message}<p class="ok">{message}</p>{/if}
      {#if error}<p class="err">{error}</p>{/if}
    </form>

    <div class="divider"></div>

    <div class="panel-head">
      <h2>Novo hábito</h2>
    </div>
    {#if showAddHabit}
      <form onsubmit={addHabit}>
        <label class="field">
          <span>Nome</span>
          <input type="text" bind:value={habitName} placeholder="Ex.: Estudo Tech" />
        </label>
        <button type="submit" class="primary">Crear</button>
      </form>
    {:else}
      <button class="ghost" onclick={() => (showAddHabit = true)}>+ Novo hábito</button>
    {/if}
  </section>
</main>

<section class="panel journal-panel">
  <div class="panel-head">
    <h2>Journal</h2>
    <p>Nota diária — markdown + frontmatter</p>
  </div>
  <form onsubmit={saveJournal}>
    <label class="field">
      <span>Data</span>
      <input type="date" bind:value={journal.date} />
    </label>
    <label class="field">
      <span>Contenido (markdown)</span>
      <textarea
        rows="4"
        bind:value={journal.content}
        placeholder="Qué hiciste hoy? Qué aprendiste?"
      ></textarea>
    </label>
    <label class="field">
      <span>Estado de ánimo</span>
      <select bind:value={journal.mood}>
        <option value="">—</option>
        <option value="great">great</option>
        <option value="good">good</option>
        <option value="neutral">neutral</option>
        <option value="bad">bad</option>
      </select>
    </label>
    <label class="field">
      <span>Tags (separadas por coma)</span>
      <input type="text" bind:value={journal.tags} placeholder="foco, tech, familia" />
    </label>
    <button type="submit" class="primary">Guardar diário</button>
    {#if journalMsg}<p class="ok">{journalMsg}</p>{/if}
  </form>

  {#if entries.length}
    <div class="divider"></div>
    <div class="panel-head">
      <h2>Entradas recientes</h2>
    </div>
    <ul class="entry-list">
      {#each entries as e}
        <li>
          <button class="entry-link" onclick={() => editEntry(e.date)}>
            <span class="entry-date">{e.date}</span>
            {#if e.mood}<span class="entry-mood">{e.mood}</span>{/if}
            <span class="entry-preview">{e.content.slice(0, 60)}</span>
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    font-feature-settings: 'cv01', 'ss03';
    background: #08090a;
    color: #f7f8f8;
  }

  /* ---- Layout ---- */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 28px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    position: sticky;
    top: 0;
    background: #0f1011;
  }
  .brand { display: flex; align-items: center; gap: 12px; }
  .dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: #5e6ad2; box-shadow: 0 0 0 4px rgba(94, 106, 210, 0.15);
  }
  .brand h1 { font-size: 18px; font-weight: 590; letter-spacing: -0.3px; margin: 0; color: #f7f8f8; }
  .sub { font-size: 12.5px; color: #8a8f98; margin: 1px 0 0; }
  .status { display: flex; align-items: center; gap: 8px; }
  .live-dot { width: 7px; height: 7px; border-radius: 50%; background: #10b981; }
  .status-text { font-size: 12.5px; color: #d0d6e0; font-weight: 510; }
  .pill {
    font-size: 12px; font-weight: 510; color: #d0d6e0;
    padding: 2px 10px; border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
  }

  main {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 340px;
    gap: 24px;
    padding: 32px 28px;
    max-width: 1180px;
    margin: 0 auto;
  }

  /* ---- Panels ---- */
  .panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 22px 24px;
  }
  .panel-head h2 { font-size: 15px; font-weight: 590; letter-spacing: -0.2px; margin: 0; color: #f7f8f8; }
  .panel-head p { font-size: 12.5px; color: #8a8f98; margin: 5px 0 0; line-height: 1.5; }
  .panel-head { margin-bottom: 20px; }

  .empty {
    padding: 40px;
    text-align: center;
    color: #8a8f98;
    font-size: 14px;
    border: 1px dashed rgba(255, 255, 255, 0.12);
    border-radius: 8px;
  }

  /* ---- Form ---- */
  .form-panel { align-self: start; }
  form { display: flex; flex-direction: column; gap: 12px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .field span { font-size: 12px; font-weight: 510; color: #d0d6e0; letter-spacing: -0.1px; }
  input, select {
    padding: 9px 12px;
    font-size: 14px;
    color: #f7f8f8;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
  }
  input::placeholder { color: #62666d; }
  input:focus, select:focus {
    outline: none;
    border-color: #5e6ad2;
    box-shadow: 0 0 0 1px rgba(94, 106, 210, 0.25);
  }

  button.primary {
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 590;
    border: none;
    border-radius: 6px;
    background: #5e6ad2;
    color: #fff;
    cursor: pointer;
  }
  button.primary:hover { background: #7170ff; }
  button.ghost {
    padding: 9px 14px;
    font-size: 13.5px;
    font-weight: 510;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    color: #d0d6e0;
    cursor: pointer;
  }
  button.ghost:hover { background: rgba(255, 255, 255, 0.05); color: #f7f8f8; }

  .divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 24px 0;
  }

  .ok { color: #10b981; font-size: 13px; margin: 2px 0 0; }
  .err { color: #ef4444; font-size: 13px; margin: 2px 0 0; }

  /* ---- Journal ---- */
  .journal-panel {
    max-width: 1180px;
    margin: 24px auto 40px;
    padding: 22px 24px;
  }
  textarea {
    padding: 9px 12px;
    font-size: 14px;
    color: #f7f8f8;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    resize: vertical;
    min-height: 90px;
  }
  textarea:focus {
    outline: none;
    border-color: #5e6ad2;
    box-shadow: 0 0 0 1px rgba(94, 106, 210, 0.25);
  }
  .entry-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 220px;
    overflow-y: auto;
  }
  .entry-link {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 7px 10px;
    text-align: left;
    font-size: 13px;
    background: transparent;
    color: #d0d6e0;
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
  }
  .entry-link:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.08);
    color: #f7f8f8;
  }
  .entry-date { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 12px; color: #8a8f98; min-width: 88px; }
  .entry-mood { font-size: 11px; font-weight: 510; color: #8a8f98; padding: 1px 6px; border: 1px solid rgba(255,255,255,0.1); border-radius: 9999px; }
  .entry-preview { flex: 1; color: #62666d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  @media (max-width: 860px) {
    header { flex-wrap: wrap; }
    main { grid-template-columns: 1fr; padding: 20px 16px; }
  }
</style>