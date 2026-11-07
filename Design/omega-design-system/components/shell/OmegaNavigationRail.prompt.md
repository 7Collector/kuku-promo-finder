# OmegaNavigationRail

The same tabs as the bottom navigation, stacked along the start edge. Shown instead of the bottom plate from a medium window up (600 wide); width alone decides. It is 96 wide, paper, with the hairline on its end edge where it meets the content.

```html
<nav class="om-nav-rail">
  <div class="om-pill-tab is-selected" role="tab" aria-selected="true">
    <span class="om-pill-tab-indicator"></span>
    <span class="om-pill-tab-icon"><i class="om-icon om-icon-home"></i></span>
    <span class="om-pill-tab-label">Home</span>
  </div>
  <!-- more .om-pill-tab, 8 apart, starting 24 below the status bar -->
</nav>
```

States: the tab states are those of `.om-pill-tab` (`.is-selected`, `.om-pill-tab--ai.is-selected`, `.om-tab-badge`); nothing forks between rail and plate except the axis.

Compose source: omega-kmp :ui, OmegaBottomNav.kt and OmegaWindow.kt, `OmegaNavigationRail(tabs, selectedKey, onSelect)`, `RailWidth`, `navigationModeFor(width)`
