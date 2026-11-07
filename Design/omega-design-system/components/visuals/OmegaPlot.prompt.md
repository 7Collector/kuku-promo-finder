Use a plot to draw up to three curves of one variable, optionally with up to three parameters the learner can drag; the curve is redrawn at the thumb with no easing, and nothing is drawn across a pole.

```html
<div class="om-plot">
  <p class="om-chart-title">The tangent</p>
  <svg class="om-chart-canvas" viewBox="0 0 292 188" style="width:292px" role="img" aria-label="Graph: The tangent. tan(x), x from −4 to 4.">
    <defs><clipPath id="plot-clip"><rect x="32" y="8" width="256" height="160"/></clipPath></defs>
    <line class="om-chart-grid" x1="96" y1="8" x2="96" y2="168"/>
    <line class="om-chart-grid is-zero" x1="32" y1="88" x2="288" y2="88"/><text class="om-chart-tick" x="24" y="92.4">0</text>
    <path class="om-plot-curve om-series-1" clip-path="url(#plot-clip)" d="M32 83 L60 70 L80 8 M84 168 L110 100 L160 88"/>
  </svg>
  <p class="om-chart-axis-name is-x">x</p>
  <div class="om-chart-legend"><span class="om-chart-legend-item om-series-1"><span class="om-chart-swatch"></span><span class="om-chart-legend-name">tan(x)</span></span></div>
</div>
```

Classes: `om-plot` (the chart frame plus the slider rows), `om-plot-curve` (2 px, clipped to the plot), and the `om-chart-*` grid, tick, label and legend classes; the plot also draws vertical gridlines, and the x axis name is the variable. Each parameter is one slider row beneath the legend (label in subhead, value in body-strong numerals, slider thumb and filled track in the accent mark, the rest sunken); the slider belongs to the actions family, so the card uses a local stand-in. Empty state: the title and "Nothing to plot in this range" in `om-chart-empty`.

Compose source: omega-kmp :ui, OmegaPlot.kt and PlotMetrics.kt, `OmegaPlot(curves, variable, domainMin, domainMax, params, title, kindLabel, emptyText)`, `PlotCurve`, `PlotParam`
