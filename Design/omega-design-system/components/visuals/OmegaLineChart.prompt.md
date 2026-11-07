Use a line chart for a value that changes over an ordered axis such as weeks or tests, for up to 4 series; the y axis follows the data and need not include zero, and a missing value breaks the line instead of being joined across.

```html
<div class="om-chart">
  <p class="om-chart-title">Class average by test</p>
  <svg class="om-chart-canvas" viewBox="0 0 628 188" style="width:628px" role="img" aria-label="Line chart: Class average by test. Test 1 62, Test 2 68, Test 3 74.">
    <line class="om-chart-grid" x1="32" y1="168" x2="624" y2="168"/><text class="om-chart-tick" x="24" y="172.4">60</text>
    <line class="om-chart-grid" x1="32" y1="8" x2="624" y2="8"/><text class="om-chart-tick" x="24" y="12.4">80</text>
    <text class="om-chart-label" x="38" y="184.4">Test 1</text>
    <path class="om-chart-line om-series-1" d="M38 152 L328 104 L618 56"/>
    <circle class="om-chart-point om-series-1" cx="38" cy="152" r="3"/>
  </svg>
</div>
```

Classes: the `om-chart` frame from the bar chart, plus `om-chart-line` (2 px, round joins and caps, no fill under it) and `om-chart-point` (radius 3, one per finite value). Points sit 6 px inside the plot at both ends. Start a new `M` subpath after a missing value. X labels thin out to every n-th when they would collide. Series colours: `om-series-1` to `om-series-9`. The line is revealed once on entry; draw the end state.

Compose source: omega-kmp :ui, OmegaCharts.kt and ChartMetrics.kt, `OmegaLineChart(series, title, xLabel, yLabel, kindLabel, emptyText, animate)`
