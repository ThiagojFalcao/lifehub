<script>
  import { api } from './api.js'
  import { hoje } from './metrics.js'

  /** Área Journal: nota diária em markdown + frontmatter, com histórico clicável. */
  let entries = $state([])
  let journal = $state({ date: hoje(), content: '', mood: '', tags: '' })
  let message = $state('')
  let error = $state('')

  async function loadJournal() {
    try {
      entries = await api('/api/journal?limit=14')
      error = ''
    } catch (e) {
      error = String(e?.message ?? e)
    }
  }

  async function salvar(e) {
    e.preventDefault()
    error = ''
    try {
      const tags = journal.tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)
      await api(`/api/journal/${journal.date}`, {
        method: 'PUT',
        body: { content: journal.content, mood: journal.mood || null, tags },
      })
      message = 'Diário salvo'
      setTimeout(() => (message = ''), 2500)
      await loadJournal()
    } catch (err) {
      const msg = String(err?.message ?? err)
      // Diário físico: limpar o editor e salvar REMOVE a entrada, e a API
      // responde 404 "Entry removed". Isso é sucesso, não erro.
      if (msg.includes('Entry removed')) {
        message = 'Entrada removida'
        setTimeout(() => (message = ''), 2500)
        await loadJournal()
        return
      }
      error = msg
    }
  }

  async function editar(d) {
    try {
      const entrada = await api(`/api/journal/${d}`)
      journal = {
        date: d,
        content: entrada.content,
        mood: entrada.mood || '',
        tags: (entrada.tags || []).join(', '),
      }
      error = ''
    } catch (e) {
      error = String(e?.message ?? e)
    }
  }

  $effect(() => {
    loadJournal()
  })
</script>

<section class="wide-panel panel">
  <div class="panel-head">
    <h2>Journal</h2>
    <p>Nota diária — markdown + frontmatter</p>
  </div>

  <form onsubmit={salvar}>
    <label class="field">
      <span>Data</span>
      <input type="date" bind:value={journal.date} />
    </label>

    <label class="field">
      <span>Conteúdo (markdown)</span>
      <textarea
        rows="4"
        bind:value={journal.content}
        placeholder="O que você fez hoje? O que aprendeu?"
      ></textarea>
    </label>

    <label class="field">
      <span>Humor</span>
      <select bind:value={journal.mood}>
        <option value="">—</option>
        <option value="great">ótimo</option>
        <option value="good">bom</option>
        <option value="neutral">neutro</option>
        <option value="bad">ruim</option>
      </select>
    </label>

    <label class="field">
      <span>Tags (separadas por vírgula)</span>
      <input type="text" bind:value={journal.tags} placeholder="foco, tech, familia" />
    </label>

    <button type="submit" class="primary">Salvar diário</button>
    {#if message}<p class="ok">{message}</p>{/if}
    {#if error}<p class="err">{error}</p>{/if}
  </form>

  {#if entries.length}
    <div class="divider"></div>
    <div class="panel-head">
      <h2>Entradas recentes</h2>
    </div>
    <ul class="entry-list">
      {#each entries as e (e.date)}
        <li>
          <button class="entry-link" onclick={() => editar(e.date)}>
            <span class="entry-date">{e.date}</span>
            {#if e.mood}<span class="entry-mood">{e.mood}</span>{/if}
            <span class="entry-preview">{(e.content || '').slice(0, 60)}</span>
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</section>
