# OmegaAdaptiveShell

The one shell every role draws: a scrolling body, the tab navigation, and the window class that arranges them. Compact (under 600 wide): the bottom plate floats over the body, which reserves its height and ends a section gap above it; the plate hides while the keyboard is up. Medium (from 600): a navigation rail on the start edge, body bottom padding 20. Expanded (from 840): a body that asked for `wide` gets the 1080 two-pane measure; otherwise it keeps the 640 measure, centred. Large is from 1200. Each inset has one owner.

```html
<div class="om-adaptive-shell om-adaptive-shell--bottom-bar">
  <!-- medium and up: <nav class="om-nav-rail">…</nav> here, and no bottom plate -->
  <div class="om-adaptive-shell-main">
    <div class="om-screen">…</div>
    <div class="om-adaptive-shell-bottom">
      <!-- optional accessory, then optional .om-action-bar, then the plate -->
      <nav class="om-bottom-nav">…</nav>
    </div>
  </div>
</div>
```

Variants: `--bottom-bar` (compact, plate shown), rail (put `.om-nav-rail` first and drop the modifier), `--wide` (two-pane measure on an expanded window), `--action-bar` (a sticky action bar is present and the body reserves its height), no navigation (sub-screens that hide the tabs: neither rail nor plate, bar row reserved).

Compose source: omega-kmp :ui, OmegaAdaptiveShell.kt and OmegaWindow.kt, `OmegaAdaptiveShell(tabs, selectedKey, onSelect, scrollState, navigationVisible, navigationVisibleWhenSplit, wide, topContentPadding, subScreen, bottomAccessory, actionBar, bottomLayer, pinnedHeader, scroll)`, `OmegaWindowClass`, `OmegaWidthClass`, `contentMeasureFor`
