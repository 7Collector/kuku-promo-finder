# OmegaProgressBar

Use for a fraction such as chapter coverage: an accent-mark fill on a sunken track, fully rounded. When there is nothing to count, draw no bar at all; an empty bar reads as 0%.

```html
<div class="om-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="72"
     aria-label="Chapter 7, 72% covered" style="--progress:72%"><div class="om-progress__fill"></div></div>
```

- `.om-progress`: 6 px tall; set `--progress` as a percentage.
- `.om-progress--on-board`: 4 px tall, board-rule track, on-board accent fill.
- At 0% leave the fill element out.
- Mark it `aria-hidden` when the row around it already announces the percentage.
- Compose can ease the fill in from zero when first shown (`animate`); the static bundle does not.

Compose source: omega-kmp :ui, BentoTile.kt, OmegaProgressBar(fraction: Float?, color, trackColor, height = 6.dp, contentDescription, animate, decorative)
