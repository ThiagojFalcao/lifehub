<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import FlorestaArea from './lib/FlorestaArea.svelte'
  import ArvoreArea from './lib/ArvoreArea.svelte'
  import JournalArea from './lib/JournalArea.svelte'

  const AREAS = [
    ['floresta', 'Floresta'],
    ['arvore', 'Árvore'],
    ['journal', 'Journal'],
  ]

  let area = $state('floresta')
  let habits = $state([])
  let forest = $state([])
  let error = $state('')

  async function load() {
    try {
      const [h, f] = await Promise.all([api('/api/habits'), api('/api/forest?days=14')])
      habits = h
      forest = f.days
      error = ''
    } catch (e) {
      error = String(e?.message ?? e)
    }
  }

  onMount(load)
</script>

<header>
  <div class="brand">
    <span class="dot" aria-hidden="true"></span>
    <div>
      <h1>LifeHub</h1>
      <p class="sub">Telemetria pessoal · local-first</p>
    </div>
  </div>

  <nav class="tabs">
    {#each AREAS as [id, rotulo] (id)}
      <button class="tab" class:active={area === id} onclick={() => (area = id)}>
        {rotulo}
      </button>
    {/each}
  </nav>

  <div class="status">
    <span class="live-dot" aria-hidden="true"></span>
    <span class="status-text">local</span>
    {#if habits.length}
      <span class="pill">{habits.length} hábitos</span>
    {/if}
  </div>
</header>

{#if error}
  <div class="banner">
    <p class="err">Não consegui falar com a API: {error}</p>
  </div>
{/if}

{#if area === 'floresta'}
  <FlorestaArea {habits} {forest} onsaved={load} />
{:else if area === 'arvore'}
  <ArvoreArea {habits} />
{:else}
  <JournalArea />
{/if}
