# ModuleTile

Use in the module grid: a neutral tile with a 22 px icon, the name on one line and a status line. The icon carries no colour family, and the name is never split mid-word.

```html
<div class="om-module-tile" role="button" aria-label="Homework, 3 pending">
  <div class="om-module-tile__top"><i class="om-icon om-icon-clipboard om-module-tile__icon"></i><span class="om-status-badge om-status-badge--neutral">3</span></div>
  <div class="om-module-tile__text"><span class="om-module-tile__name">Homework</span><span class="om-module-tile__meta">3 pending</span></div>
</div>
```

- Surface, radius lg, 16 padding, 12 between the icon row and the text.
- Badge (optional): a neutral status badge with a count at the top end.
- Compact mode: when there is a badge, leave `__meta` out; the badge stands for it. Keep the full phrase in `aria-label`.
- `:active` or `.is-pressed`: ink ripple and the 0.98 scale. The tile is always tappable.
- Sized to its content; a tile grid makes its tiles equal.

Compose source: omega-kmp :ui, TimelineRow.kt, ModuleTile(name, meta, icon, onClick, badge, contentDescription), moduleTileShowsMeta(hasBadge, compact)
