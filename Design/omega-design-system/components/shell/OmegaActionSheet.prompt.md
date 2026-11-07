# OmegaActionSheet and OmegaBottomSheet

A modal sheet over a scrim: surface, top corners xl, the sheet shadow (the only shadow in the system), a decorative handle, a title row with a 48 close button, scrollable content, and an optional sticky action bar that stays put while the content scrolls. The sheet owns the bottom insets once; the scrim is a sibling behind it, never its parent. `OmegaBottomSheet` is the same sheet under its older name.

```html
<div class="om-scrim"></div>
<section class="om-action-sheet" role="dialog" aria-label="Mark Diya absent">
  <div class="om-sheet-handle"></div>
  <div class="om-sheet-title-row">
    <h2 class="om-sheet-title">Mark Diya absent</h2>
    <button class="om-sheet-close" aria-label="Close"><i class="om-icon om-icon-close"></i></button>
  </div>
  <div class="om-sheet-content">…</div>
  <div class="om-sheet-actions"><!-- full-width primary button --></div>
</section>
```

Variants: with `.om-sheet-actions` (hairline above, padding 12/20/16; the content then ends 16 above it) or without (content is its own choices and ends 20 above the bottom); `.om-bottom-sheet` is an alias of `.om-action-sheet`. Height is capped at 88% of the window above the keyboard. Arrives with a slide up and a scrim fade, instant under reduced motion; no drag to dismiss and no exit animation.

Compose source: omega-kmp :ui, OmegaActionSheet.kt and OmegaBottomSheet.kt, `OmegaActionSheet(title, onDismiss, dismissLabel, actions, content)`, `OmegaBottomSheet(…)` with the same parameters
