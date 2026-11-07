Use a donut for one fraction of a whole next to its name, such as chapters covered; the colour is the caller's (a subject or status colour) and the figure in the middle is the whole percentage.

```html
<span class="om-donut" style="color:var(--subject-1)" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="72" aria-label="Mathematics, 72% covered">
  <svg class="om-donut-ring" viewBox="0 0 48 48" aria-hidden="true">
    <circle class="om-donut-track" cx="24" cy="24" r="20"/>
    <circle class="om-donut-arc" cx="24" cy="24" r="20" pathLength="360" stroke-dasharray="259.2 360" transform="rotate(-90 24 24)"/>
  </svg>
  <span class="om-donut-figure">72%</span>
</span>
```

Classes: `om-donut` (48 by default; `--donut-size` for another size, ring and stroke scale with it; `--donut-track` for a track other than sunken), `om-donut-ring`, `om-donut-track`, `om-donut-arc` (round cap, starts at 12 o'clock, dash length = fraction × 360), `om-donut-figure` (leave it out for `showFigure = false`). The fraction is clamped to 0 to 1, and anything below 1 never rounds up to 100%. The sweep animates once; draw the end state.

Compose source: omega-kmp :ui, DonutProgress.kt, `DonutProgress(fraction, color, size = 48.dp, trackColor, label, animate, showFigure)`
