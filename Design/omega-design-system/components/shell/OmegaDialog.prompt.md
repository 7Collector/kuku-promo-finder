# OmegaDialog and OmegaConfirmDialog

A modal dialog: scrim, a centred surface card (radius xl, 24 padding, no shadow), a title, body content and an optional end-aligned action row. Its width is capped at 420 including 24 side gaps, so it never stretches on a tablet. Use the confirm variant before a destructive action; the confirm button's own word ("Discard", "Sign out") is the signal, and the colour only reinforces it.

```html
<div class="om-scrim"></div>
<div class="om-dialog-host">
  <section class="om-dialog" role="dialog" aria-label="Discard draft?">
    <h2 class="om-dialog-title">Discard draft?</h2>
    <p class="om-dialog-message">This homework hasn't been published yet. Discarding removes it for every class you picked.</p>
    <div class="om-dialog-actions"><!-- tertiary Cancel, then primary confirm --></div>
  </section>
</div>
```

Variants: no action row (dismissed by the scrim or back only); confirm (tertiary cancel, primary confirm, 8 apart, 20 above); destructive confirm (the confirm button is filled with `--danger-strong` with `--surface` text: the one place a filled danger button exists). Tall content scrolls inside the card. No enter animation.

Compose source: omega-kmp :ui, OmegaDialog.kt, `OmegaDialog(title, onDismiss, dismissLabel, actions, content)`, `OmegaConfirmDialog(title, message, confirmLabel, onConfirm, onCancel, cancelLabel, destructive)`
