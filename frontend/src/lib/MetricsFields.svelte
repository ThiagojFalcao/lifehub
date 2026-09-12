<script>
  import { inputType, isNumeric } from './metrics.js'

  /** Campos dinâmicos a partir do `metrics_schema` do hábito selecionado. */
  let { schema = {}, values = $bindable({}) } = $props()

  let campos = $derived(Object.entries(schema || {}))
</script>

{#if campos.length}
  {#each campos as [nome, tipo] (nome)}
    {#if tipo === 'bool'}
      <label class="field">
        <span class="check-row">
          <input type="checkbox" bind:checked={values[nome]} />
          <span>{nome}</span>
        </span>
      </label>
    {:else}
      <label class="field">
        <span>{nome}<em>{tipo}</em></span>
        <input
          type={inputType(tipo)}
          step={isNumeric(tipo) && tipo !== 'int' ? 'any' : undefined}
          bind:value={values[nome]}
          placeholder={tipo === 'str' ? 'texto livre' : 'nº'}
        />
      </label>
    {/if}
  {/each}
{:else}
  <p class="hint">Este hábito não declara métricas — só duração e notas.</p>
{/if}
