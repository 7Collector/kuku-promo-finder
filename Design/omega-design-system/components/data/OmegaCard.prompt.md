# OmegaCard

Use for the card most content sits on: surface on paper, radius lg, no shadow and no outline. When it is tappable, make the whole card the one target rather than a strip inside it.

```html
<div class="om-card">…</div>
<div class="om-card om-card--tappable" role="button" aria-label="Term 1 report">…</div>
<div class="om-card om-card--outlined">…</div>
```

- `.om-card`: 16 padding, surface fill.
- `.om-card--tappable`: 48 minimum; `:active` or `.is-pressed` gives the ink ripple and the 0.98 scale.
- `.om-card--outlined`: an outline over the fill for a card that must stand out from identical neighbours. Set `--card-border` (the caller's colour; the apps pass outline or hairline) and `--card-border-width` (2 px by default).
- Background, shape and padding are parameters in Compose; override the matching CSS property when a screen needs it.

Compose source: omega-kmp :ui, BentoTile.kt, OmegaCard(onClick, contentDescription, background, border, borderWidth = 2.dp, shape, contentPadding = 16.dp)
