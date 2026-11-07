# TileGrid

Use for a small fixed-column grid of tiles inside a screen that already scrolls. Every tile is as tall as the tallest tile in the whole grid, not just its own row.

```html
<div class="om-tile-grid om-tile-grid--2">
  <div class="om-module-tile">…</div>
  <div class="om-module-tile">…</div>
  <div class="om-module-tile">…</div>
</div>
```

- `.om-tile-grid--1`, `--2`, `--3`, or set `--columns`. Two columns under 480 px of width, three from there; one in compact mode.
- 11 px gap in both directions.
- A tile in a short last row keeps its own column width; it is not stretched across the row.
- With no tiles, draw nothing at all, not an empty box.

Compose source: omega-kmp :ui, TileGrid.kt, TileGrid(items, columns, horizontalSpacing = 11.dp, verticalSpacing = 11.dp, tile), adaptiveColumnsFor(widthDp)
