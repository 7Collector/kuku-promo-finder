# OmegaFigureStrip

Use for a row of glanceable counts on one flat surface, divided by hairlines, instead of several narrow tiles. Lead with the figure; only the qualifier line carries the tone, the figure and label stay ink.

```html
<div class="om-figure-strip">
  <div class="om-figure-cell om-figure-cell--danger om-figure-cell--tappable" role="button" aria-label="2 homeworks, Overdue">
    <div class="om-figure-cell__top"><span class="om-figure-cell__figure">2</span></div>
    <div class="om-figure-cell__bottom"><p class="om-figure-cell__label">homeworks</p><p class="om-figure-cell__meta">Overdue</p></div>
  </div>
  <span class="om-figure-divider"></span>
  <div class="om-figure-cell om-figure-cell--warning">…</div>
</div>
```

- Strip: surface, radius lg, 96 minimum height; cells share the width equally and are as tall as the tallest.
- Cell tone (colours the qualifier only): `--info`, `--help`, `--tip`, `--success`, `--warning`, `--danger`, `--neutral`.
- `.om-figure-cell__icon`: an optional 18 px icon in ink 2 at the top end.
- `.om-figure-cell--tappable` with `:active` or `.is-pressed`: ink ripple only. Each cell is its own target.
- Put a `.om-figure-divider` between neighbours.

Compose source: omega-kmp :ui, OmegaFigureStrip.kt, OmegaFigureStrip(minHeight = 96.dp, cells), FigureCell(figure, label, meta, ink, icon, onClick, contentDescription), FigureDivider()
