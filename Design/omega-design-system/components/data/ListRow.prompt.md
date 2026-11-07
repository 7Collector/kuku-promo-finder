# ListRow

Use for one row of a grouped list. The rule that matters: a status badge never sits beside the title, it takes a meta row above it, so wrapping text keeps the row's whole width.

```html
<div class="om-list-row om-list-row--two-line om-list-row--tappable" role="button">
  <div class="om-list-row__main">
    <div class="om-list-row__leading"><i class="om-icon om-icon-clipboard"></i></div>
    <div class="om-list-row__text">
      <div class="om-list-row__meta-row"><span class="om-list-row__meta">Chemistry</span><span class="om-status-badge om-status-badge--warning">Due today</span></div>
      <div class="om-list-row__title-row"><span class="om-list-row__title">Chemistry worksheet</span><i class="om-icon om-icon-chevron-right om-list-chevron"></i></div>
      <span class="om-list-row__supporting">Submit by 23:59</span>
    </div>
  </div>
</div>
```

- `.om-list-row--two-line`: 72 minimum and top-aligned; use whenever there is a supporting line, meta or badge. Without it the row is 56 and centred.
- `.om-list-row--with-leading`: starts the hairline at the text keyline (68) past the 40 px leading slot.
- `.om-list-row--last`: no hairline. `.om-list-row--selected`: accent container, for the row whose detail is open beside the list.
- `.om-list-row--tappable` with `:active` or `.is-pressed`: ink ripple only, no scale.
- Trailing placement: badge in `__meta-row`; chevron (`.om-list-chevron`, 20, ink 3), switch or short value (`__value`) in `__title-row`; a button, or a value in compact mode, in `__below` under the text.
- Title clamps at three lines, supporting at two (`__supporting--full` lifts the clamp).

Compose source: omega-kmp :ui, OmegaList.kt, ListRow(title, supporting, meta, badge, leading, trailing, trailingKind: ListRowTrailing, onClick, divider, selected, supportingMaxLines), ListRowChevron(), listRowTrailingPlacement(kind, compact)
