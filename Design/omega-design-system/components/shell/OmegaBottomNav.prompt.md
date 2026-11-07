# OmegaBottomNav and PillTab

The bottom navigation of a compact window: paper, a hairline on the top edge, no shadow, 64 of tabs above the navigation-bar inset, which it owns. Tabs share the width equally and every label is always shown. A single tab is never drawn.

```html
<nav class="om-bottom-nav">
  <div class="om-pill-tab is-selected" role="tab" aria-selected="true">
    <span class="om-pill-tab-indicator"></span>
    <span class="om-pill-tab-icon"><i class="om-icon om-icon-home"></i></span>
    <span class="om-pill-tab-label">Home</span>
  </div>
  <div class="om-pill-tab" role="tab" aria-label="Routine, 3 new">
    <span class="om-pill-tab-indicator"></span>
    <span class="om-pill-tab-icon"><i class="om-icon om-icon-calendar"></i><span class="om-tab-badge">3</span></span>
    <span class="om-pill-tab-label">Routine</span>
  </div>
</nav>
```

States: `.is-selected` (ink icon and label at weight 500, 16 by 3 accent indicator; unselected is ink-3 at weight 400 with a transparent indicator); `.om-pill-tab--ai.is-selected` (the glyph alone takes the AI gradient, and only while selected); `.om-tab-badge` (ink pill with paper digits over the icon's top end corner, "99+" past 99; the tab does not grow, and the count must also be in the tab's spoken name).

Compose source: omega-kmp :ui, OmegaBottomNav.kt, `OmegaBottomNav(tabs, selectedKey, onSelect)`, `PillTab(label, icon, selected, selectedIcon, isAi, badge)`, `OmegaTab`, `OmegaTabBadge(count, description)`
