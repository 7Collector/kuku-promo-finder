Use on-stage glass for a small raised element that sits on the dark board, such as a pill, a time chip or a stat tile; it is a flat raised fill with a hairline rule, not a blur.

```html
<span class="om-on-stage-glass" style="border-radius:var(--radius-full);padding:4px 12px">Class teacher</span>
```

Classes: `om-on-stage-glass` (board-raised fill, 1 px board-rule border). The element supplies its own `border-radius`, padding and text colour (on-board roles). Use it only on the board; on paper use a surface instead. No backdrop blur, no translucency, no shadow.

Compose source: omega-kmp :ui, OnStageGlass.kt, `Modifier.onStageGlass(shape)` (the `strong` parameter is unused)
