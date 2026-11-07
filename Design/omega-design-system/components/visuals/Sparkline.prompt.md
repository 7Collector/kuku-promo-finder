Use a sparkline beside a figure to show its direction over time; it has no axis and no values, so it never stands alone.

```html
<svg class="om-sparkline" viewBox="0 0 64 24" role="img" aria-label="Attendance, last 8 weeks, rising">
  <path class="om-sparkline-line" d="M2.25 21.75 L19.25 14.44 L36.25 12 L53.25 4.69 L61.75 2.25"/>
  <circle class="om-sparkline-dot" cx="61.75" cy="2.25" r="2.25"/>
</svg>
```

Classes: `om-sparkline` (64 by 24 by default; set `width`/`height` and the `viewBox` together for another size), `om-sparkline-line` (1.5 px, round), `om-sparkline-dot` (radius 2.25 on the last value). The drawing is inset by the dot radius on every side. A flat series runs through the middle; a single value is the dot alone; a missing value breaks the line. Colour is the accent mark by default; set `color` on the svg for another role (for example `var(--success)`, or `var(--accent-mark-on-board)` on a board). Use `aria-hidden="true"` when the figure beside it already says the same thing.

Compose source: omega-kmp :ui, OmegaCharts.kt, `Sparkline(values, contentDescription, color, width, height, animate)`
