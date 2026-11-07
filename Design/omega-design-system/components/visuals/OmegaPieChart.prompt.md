Use a pie chart only for parts of one whole with a handful of slices; the legend carries the numbers, so every slice has a list row reading "value · share%".

```html
<div class="om-chart">
  <p class="om-chart-title">Attendance today</p>
  <svg class="om-pie" viewBox="0 0 160 160" role="img" aria-label="Pie chart: Attendance today. Present 412, 88%. Absent 54, 12%.">
    <path class="om-pie-slice om-series-1" d="M80 80 L80 0 A80 80 0 1 1 26.76 20.28 Z"/>
    <path class="om-pie-slice om-series-2" d="M80 80 L26.76 20.28 A80 80 0 0 1 80 0 Z"/>
    <line class="om-pie-gap" x1="80" y1="80" x2="80" y2="0"/><line class="om-pie-gap" x1="80" y1="80" x2="26.76" y2="20.28"/>
  </svg>
  <div class="om-chart-legend is-list">
    <span class="om-chart-legend-item om-series-1"><span class="om-chart-swatch"></span><span class="om-chart-legend-name">Present</span><span class="om-chart-legend-figure">412 · 88%</span></span>
  </div>
</div>
```

Classes: `om-pie` (160 across, solid, no hole), `om-pie-slice`, `om-pie-gap` (a 2 px surface line at each slice start, only when there is more than one slice), `om-chart-legend is-list`, `om-chart-legend-figure`. Slices start at 12 o'clock and run clockwise in data order. A share under one per cent reads "<1%". No labels on the slices, no exploded slice. The pie sweeps in once; draw the end state.

Compose source: omega-kmp :ui, OmegaCharts.kt, `OmegaPieChart(points, title, kindLabel, emptyText, animate)`
