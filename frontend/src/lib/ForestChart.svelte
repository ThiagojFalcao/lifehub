<script>
  let { days = [] } = $props()

  const W = 760
  const H = 300
  const PAD = { l: 44, r: 16, t: 20, b: 34 }
  const palette = { green: '#10b981', yellow: '#eab308', red: '#e5484d' }
  const gridColor = 'rgba(255,255,255,0.06)'
  const labelColor = '#8a8f98'

  let innerW = $derived(W - PAD.l - PAD.r)
  let innerH = $derived(H - PAD.t - PAD.b)
  let barW = $derived(days.length ? innerW / days.length : 1)
  let max = $derived(Math.max(4, ...days.map((d) => Math.max(d.completed, d.avg_7d))))
  let x = $derived((i) => PAD.l + i * barW + barW / 2)
  let y = $derived((v) => PAD.t + innerH - (v / max) * innerH)
  let barX = $derived((i) => PAD.l + i * barW + barW * 0.18)
  let barWidth = $derived(days.length ? barW * 0.64 : 0)
  let trend = $derived(days.map((d, i) => `${x(i)},${y(d.avg_7d)}`).join(' '))
  let gridY = $derived([0, 0.25, 0.5, 0.75, 1].map((f) => PAD.t + innerH - f * innerH))

  let hover = $state(-1)
</script>

<svg
  width={W}
  height={H}
  viewBox={`0 0 ${W} ${H}`}
  role="img"
  aria-label="Floresta — hábitos completados por dia"
  onmouseleave={() => (hover = -1)}
>
  <!-- grid horizontal sutil (4 linhas) -->
  {#each gridY as gy}
    <line x1={PAD.l} y1={gy} x2={W - PAD.r} y2={gy} stroke={gridColor} stroke-width="1" stroke-dasharray="3 4" />
  {/each}

  {#each days as d, i}
    {@const bh = d.completed === 0 ? 2 : PAD.t + innerH - y(d.completed)}
    <rect
      x={barX(i)}
      y={d.completed === 0 ? PAD.t + innerH - 2 : y(d.completed)}
      width={barWidth}
      height={bh}
      fill={palette[d.color] ?? '#62666d'}
      rx="1.5"
      opacity={hover === -1 || hover === i ? 1 : 0.45}
    >
      <title>{d.date} — {d.completed} habitos</title>
    </rect>
    <text x={x(i)} y={H - 12} text-anchor="middle" font-size="10" fill={labelColor} font-family="JetBrains Mono, monospace">
      {d.date.slice(5)}
    </text>
  {/each}

  <polyline points={trend} fill="none" stroke="#7170ff" stroke-width="1.8" stroke-linejoin="round" />

  <!-- dots da tendência -->
  {#each days as d, i}
    <circle cx={x(i)} cy={y(d.avg_7d)} r="2.4" fill="#7170ff" opacity="0.8" />
  {/each}
</svg>

<style>
  svg { display: block; }
</style>