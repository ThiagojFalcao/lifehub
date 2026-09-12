<script>
  import { api } from './api.js'

  /** Novo hábito: categoria real, floor plan e editor do schema de métricas. */
  let { onsaved } = $props()

  const CATEGORIAS = [
    ['study_tech', 'Estudo / Tech'],
    ['gym', 'Treino'],
    ['wellness', 'Bem-estar'],
    ['creative', 'Criativo'],
    ['work', 'Trabalho'],
    ['misc', 'Outro'],
  ]
  const TIPOS = ['int', 'float', 'str', 'bool']

  let aberto = $state(false)
  let nome = $state('')
  let categoria = $state('study_tech')
  let categoriaLivre = $state('')
  let floorPlan = $state('')
  let campos = $state([{ nome: '', tipo: 'int' }])
  let error = $state('')
  let enviando = $state(false)

  function addCampo() {
    campos.push({ nome: '', tipo: 'int' })
  }

  function removeCampo(i) {
    if (campos.length === 1) {
      campos[0] = { nome: '', tipo: 'int' }
      return
    }
    campos.splice(i, 1)
  }

  function reset() {
    nome = ''
    categoria = 'study_tech'
    categoriaLivre = ''
    floorPlan = ''
    campos = [{ nome: '', tipo: 'int' }]
    error = ''
  }

  async function criar(e) {
    e.preventDefault()
    error = ''
    const nomeLimpo = nome.trim()
    if (!nomeLimpo) {
      error = 'O nome é obrigatório.'
      return
    }
    const metricsSchema = {}
    for (const c of campos) {
      const n = c.nome.trim()
      if (n) metricsSchema[n] = c.tipo
    }
    const cat = categoria === 'outra' ? categoriaLivre.trim() || 'misc' : categoria

    enviando = true
    try {
      await api('/api/habits', {
        method: 'POST',
        body: {
          name: nomeLimpo,
          category: cat,
          metrics_schema: metricsSchema,
          floor_plan: floorPlan.trim() || null,
        },
      })
      reset()
      aberto = false
      onsaved?.()
    } catch (err) {
      error = String(err?.message ?? err)
    } finally {
      enviando = false
    }
  }
</script>

<div class="divider"></div>

<div class="panel-head">
  <h2>Novo hábito</h2>
  <p>O que este hábito mede além da duração?</p>
</div>

{#if aberto}
  <form onsubmit={criar}>
    <label class="field">
      <span>Nome</span>
      <input type="text" bind:value={nome} placeholder="Ex.: Estudo Tech" />
    </label>

    <label class="field">
      <span>Categoria</span>
      <select bind:value={categoria}>
        {#each CATEGORIAS as [valor, rotulo] (valor)}
          <option value={valor}>{rotulo}</option>
        {/each}
        <option value="outra">Outra…</option>
      </select>
    </label>

    {#if categoria === 'outra'}
      <label class="field">
        <span>Categoria personalizada</span>
        <input type="text" bind:value={categoriaLivre} placeholder="Ex.: musica" />
      </label>
    {/if}

    <label class="field">
      <span>Floor plan</span>
      <input
        type="text"
        bind:value={floorPlan}
        placeholder="Ex.: 10 min de revisão, mesmo nos dias ruins"
      />
    </label>

    <div class="panel-head" style="margin:18px 0 10px">
      <h2>Métricas</h2>
      <p>Cada linha vira um campo no registro de sessão.</p>
    </div>

    {#each campos as campo, i}
      <div class="metric-row">
        <input type="text" bind:value={campo.nome} placeholder="nome (ex.: focus_minutes)" />
        <select bind:value={campo.tipo}>
          {#each TIPOS as t (t)}<option value={t}>{t}</option>{/each}
        </select>
        <button
          type="button"
          class="metric-remove"
          onclick={() => removeCampo(i)}
          aria-label="Remover métrica"
          title="Remover métrica"
        >
          ×
        </button>
      </div>
    {/each}

    <button type="button" class="ghost" onclick={addCampo}>+ Adicionar métrica</button>

    <button type="submit" class="primary" disabled={enviando}>
      {enviando ? 'Criando…' : 'Criar hábito'}
    </button>

    {#if error}<p class="err">{error}</p>{/if}
    <button type="button" class="ghost" onclick={() => (aberto = false)}>Cancelar</button>
  </form>
{:else}
  <button class="ghost" onclick={() => (aberto = true)}>+ Novo hábito</button>
{/if}