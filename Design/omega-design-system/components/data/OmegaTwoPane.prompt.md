# OmegaTwoPane

Use for a main pane beside a supporting pane. It splits 3:2 only when the window is a two-pane window and the slot is at least 720 px wide; otherwise the supporting pane stacks under the main one.

```html
<div class="om-two-pane om-two-pane--split">
  <div class="om-two-pane__main">…</div>
  <div class="om-two-pane__supporting">…</div>
</div>
```

- `.om-two-pane`: stacked, 20 between the panes.
- `.om-two-pane--split`: side by side, 24 gutter, flex 3 to 2. Apply it only from a 720 px slot.
- Leave the supporting pane out of the stacked markup when it only restates the main pane (`stackedSupporting = false`).
- The switch is the caller's: CSS here does not measure the slot.

Compose source: omega-kmp :ui, OmegaSurface.kt, OmegaTwoPane(mainWeight = 3f, supportingWeight = 2f, stackedSpacing = 20.dp, stackedSupporting), TwoPaneMinWidth = 720.dp, PaneGutter()
