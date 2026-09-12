<script>
  /** Gráfico da Árvore: minutos investidos por dia + tendência de 7 dias. */
  let { days = [] } = $props()

  const W = 760
  const H = 300
  const PAD = { l: 48, r: 16, t: 20, b: 34 }
  const palette = { green: '#10b981', yellow: '#eab308', red: '#e5484d' }
  const gridColor = 'rgba(255,255,255,0.06)'
  const labelColor = '#8a8f98'

  let innerW = $derived(W - PAD.l - PAD.r)
  let innerH = $derived(H - PAD.t - PAD.b)
  let barW = $derived(days.length ? innerW / days.length : 1)
  let max = $derived(Math.max(10, ...days.map((d) => Math.max(d.duration_min, d.avg_7d_min))))
  let x = $derived((i) => PAD.l + i * barW + barW / 2)
  let y = $derived((v) => PAD.t + innerH - (v / max) * innerH)
  let barX = $derived((i) => PAD.l + i * barW + barW * 0.18)
  let barWidth = $derived(days.length ? barW * 0.64 : 0)
  let trend = $derived(days.map((d, i) => `${x(i)},${y(d.avg_7d_min)}`).join(' '))
  let gridY = $derived([0, 0.25, 0.5, 0.75, 1].map((f) => PAD.t + innerH - f * innerH))
  // Com muitos dias o rótulo do eixo X vira sopa de letras: mostra 1 a cada N.
  let passo = $derived(Math.max(1, Math.ceil(days.length / 14)))
</script>

<svg
  width={W}
  height={H}
  viewBox={`0 0 ${W} ${H}`}
  role="img"
  aria-label="Árvore — minutos investidos por dia"
>
  {#each gridY as gy}
    <line
      x1={PAD.l}
      y1={gy}
      x2={W - PAD.r}
      y2={gy}
      stroke={gridColor}
      stroke-width="1"
      stroke-dasharray="3 4"
    />
  {/each}

  <text x={PAD.l - 8} y={PAD.t + 4} text-anchor="end" font-size="9.5" fill={labelColor}>
    {Math.round(max)}
  </text>
  <text x={PAD.l - 8} y={PAD.t + innerH / 2 + 3} text-anchor="end" font-size="9.5" fill={labelColor}>
    {Math.round(max / 2)}
  </text>
  <text x={PAD.l - 8} y={PAD.t + innerH + 3} text-anchor="end" font-size="9.5" fill={labelColor}>
    0
  </text>

  {#each days as d, i}
    {@const bh = d.duration_min === 0 ? 2 : PAD.t + innerH - y(d.duration_min)}
    <rect
      x={barX(i)}
      y={d.duration_min === 0 ? PAD.t + innerH - 2 : y(d.duration_min)}
      width={barWidth}
      height={bh}
      fill={palette[d.color] ?? '#62666d'}
      rx="1.5"
    >
      <title>{d.date} — {d.duration_min} min · {d.sessions} sessão(ões)</title>
    </rect>
    {#if i % passo === 0}
      <text
        x={x(i)}
        y={H - 12}
        text-anchor="middle"
        font-size="10"
        fill={labelColor}
        font-family="JetBrains Mono, monospace"
      >
        {d.date.slice(5)}
      </text>
    {/if}
  {/each}

  <polyline points={trend} fill="none" stroke="#7170ff" stroke-width="1.8" stroke-linejoin="round" />
  {#each days as d, i}
    <circle cx={x(i)} cy={y(d.avg_7d_min)} r="2.4" fill="#7170ff" opacity="0.8" />
  {/each}
</svg>

<div class="legend">
  <span class="legend-item"><span class="legend-swatch" style="background:#10b981"></span> no ritmo</span>
  <span class="legend-item"><span class="legend-swatch" style="background:#eab308"></span> abaixo</span>
  <span class="legend-item"><span class="legend-swatch" style="background:#e5484d"></span> parado</span>
  <span class="legend-item"><span class="legend-line"></span> média móvel de 7 dias (min)</span>
</div>

<style>
  svg {
    display: block;
    width: 100%;
    height: auto;
  }
</style>