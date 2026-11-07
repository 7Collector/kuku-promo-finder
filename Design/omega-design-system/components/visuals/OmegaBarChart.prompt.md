Use a bar chart to compare amounts across a few named categories, for up to 4 series and 24 points; bars are plain rectangles measured from zero, and the first series is always the accent mark.

```html
<div class="om-chart">
  <p class="om-chart-title">Marks by subject</p>
  <p class="om-chart-axis-name">Average marks, out of 100</p>
  <svg class="om-chart-canvas" viewBox="0 0 628 188" style="width:628px" role="img" aria-label="Bar chart: Marks by subject. Maths 78, Science 71.">
    <line class="om-chart-grid is-zero" x1="32" y1="168" x2="624" y2="168"/><text class="om-chart-tick" x="24" y="172.4">0</text>
    <line class="om-chart-grid" x1="32" y1="8" x2="624" y2="8"/><text class="om-chart-tick" x="24" y="12.4">100</text>
    <text class="om-chart-label" x="91.2" y="184.4">Maths</text>
    <rect class="om-chart-bar om-series-1" x="46.2" y="43.2" width="45" height="124.8"/>
  </svg>
  <p class="om-chart-axis-name is-x">Subject</p>
  <div class="om-chart-legend"><span class="om-chart-legend-item om-series-1"><span class="om-chart-swatch"></span><span class="om-chart-legend-name">Term 1</span></span></div>
</div>
```

Classes: `om-chart` (frame, gap 8), `om-chart-title`, `om-chart-axis-name` (`is-x` centres it under the plot), `om-chart-canvas` (188 tall: plot from y 8 to 168, gutter = widest tick + 8, right inset 4), `om-chart-grid` (`is-zero` for the zero line), `om-chart-tick`, `om-chart-label`, `om-chart-bar`, `om-chart-legend` (shown for two or more series), `om-chart-empty` ("No data to show" replaces the drawing). Colour comes from `om-series-1` to `om-series-9`. No corner radius on bars, no shadow, no value labels on bars. The bars grow once on entry; draw the end state.

Compose source: omega-kmp :ui, OmegaCharts.kt and ChartMetrics.kt, `OmegaBarChart(series, title, xLabel, yLabel, kindLabel, emptyText, animate)`, `ChartSeries`, `ChartPoint`, `chartSeriesColor(index)`
