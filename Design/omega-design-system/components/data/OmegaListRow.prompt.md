# OmegaListRow

The simple, older form of a list row: optional leading, a title over one supporting line, optional trailing. Prefer ListRow for new rows; use OmegaListEntry (the bare `.om-list-row`) when a row needs custom content.

```html
<div class="om-list-row om-list-row--simple om-list-row--tappable" role="button">
  <div class="om-list-row__main">
    <div class="om-list-row__text"><span class="om-list-row__title">Class 8B</span><span class="om-list-row__supporting">Mathematics, 34 students</span></div>
    <i class="om-icon om-icon-chevron-right om-list-chevron"></i>
  </div>
</div>
```

- `.om-list-row`: the entry itself. 12 by 16 padding, 48 minimum, hairline beneath from the content's start (set `--_inset` to move it).
- `.om-list-row--simple`: always centred, leading slot unboxed, title clamps at two lines.
- `.om-list-row--selected`, `.om-list-row--last`, `.om-list-row--tappable` (`.is-pressed`): as on ListRow.
- Title and supporting colours are parameters in Compose (ink and ink 2 by default); override `color` on the element.

Compose source: omega-kmp :ui, OmegaSurface.kt, OmegaListRow(title, meta, onClick, divider, selected, titleColor, metaColor, metaMaxLines = 2, leading, trailing), OmegaListEntry(onClick, divider, selected, contentPadding, dividerInset)
