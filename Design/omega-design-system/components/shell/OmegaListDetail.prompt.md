# OmegaListDetail and OmegaDetailPlaceholder

A catalog beside the item it opened. Two panes only when the window is expanded or larger (from 840 wide) and the slot itself is at least 720 wide; otherwise one pane, showing the open item alone or the list alone. Beside its list a detail drops its back control, and an empty detail pane shows the placeholder, never a blank.

```html
<div class="om-list-detail">
  <div class="om-list-detail-list"><!-- the catalog --></div>
  <div class="om-list-detail-detail">
    <div class="om-detail-placeholder">
      <div class="om-detail-placeholder-message">Choose a homework to see who has submitted it.</div>
    </div>
  </div>
</div>
```

Variants: two panes (default: list to detail 2:3, 24 gutter, top aligned); `.om-list-detail--single` (one pane; render only the detail, or only the list). `.om-detail-placeholder` is a sunken, radius md surface with 24 padding, at least 200 tall, one centred ink-2 body sentence; it is never drawn on a phone.

Compose source: omega-kmp :ui, OmegaListDetail.kt, `OmegaListDetail(listWeight, detailWeight, detail, placeholder, list)`, `OmegaDetailPlaceholder(message)`, `OmegaPane`, `TwoPaneMinWidth`
