# OmegaActionBar

The persistent bar a long authoring screen ends in: one quiet action and one solid commit, always visible without scrolling. It is opaque paper with a drawn 1 px outline line on its top edge, never translucent and never separated by a tint step. It owns the keyboard and navigation-bar insets and rides on the keyboard; the body above reserves its height.

```html
<div class="om-action-bar">
  <div class="om-action-bar-info">36 present · 2 absent</div>
  <!-- quiet action (tertiary button), optional -->
  <!-- commit action (primary button), last -->
</div>
```

Layout: a row, 10 gap, centred vertically, padding 8 top, 20 sides, 10 bottom. Give the informational part the remaining width (`.om-action-bar-info`) and put the commit last so it keeps its size. Inside `.om-adaptive-shell-bottom` it sits directly above the bottom plate, which then owns the navigation bar; add `.om-adaptive-shell--action-bar` to the shell.

Compose source: omega-kmp :ui, OmegaActionBar.kt, `OmegaActionBar(content: RowScope)`; hosted by `OmegaAdaptiveShell(actionBar = …)`
