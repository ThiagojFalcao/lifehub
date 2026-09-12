<script>
  let { days = [] } = $props()

  const W = 640
  const H = 260
  const PAD = 28
  const barW = days.length ? (W - PAD * 2) / days.length : 1
  const palette = { green: '#22c55e', yellow: '#eab308', red: '#ef4444' }

  const max = Math.max(10, ...days.map((d) => Math.max(d.completed, d.avg_7d)))
  const x = (i) => PAD + i * barW + barW / 2
  const y = (v) => H - PAD - (v / max) * (H - PAD * 2)
  const barX = (i) => PAD + i * barW + barW * 0.15
  const barWidth = days.length ? barW * 0.7 : 0
  const trend = days.map((d, i) => `${x(i)},${y(d.avg_7d)}`).join(' ')
</script>

<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Floresta">
  {#each days as d, i}
    {@const bh = d.completed === 0 ? 2 : H - PAD - y(d.completed)}
    <rect
      x={barX(i)}
      y={d.completed === 0 ? H - PAD - 2 : y(d.completed)}
      width={barWidth}
      height={bh}
      fill={palette[d.color] ?? '#888'}
      rx="2"
    />
    <text x={x(i)} y={H - PAD + 14} text-anchor="middle" font-size="10" fill="#888">
      {d.date.slice(5)}
    </text>
  {/each}
  <polyline points={trend} fill="none" stroke="#3b82f6" stroke-width="2" />
</svg>