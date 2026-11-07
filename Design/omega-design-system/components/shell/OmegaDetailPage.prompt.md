# OmegaDetailPage

A full-screen page outside the tabbed shell, such as a detail a role opens over its tabs. It is a screen scaffold with the bar row always reserved, held to the same 640 reading measure so a tablet does not stretch it. The bar owns the status bar; the body owns the keyboard and the navigation bar.

```html
<div class="om-screen om-detail-page">
  <header class="om-screen-bar"><div class="om-screen-bar-row">
    <button class="om-back-button" aria-label="Back to requests"><i class="om-icon om-icon-chevron-left"></i></button>
    <div class="om-screen-bar-title-slot"></div>
  </div></header>
  <div class="om-screen-body"><div class="om-screen-content">…</div></div>
</div>
```

Variants: default body padding is 8 under the bar, 20 at the bottom, page margin at the sides; `.om-screen-content--flush-top` for a page whose first child is a full-bleed header (`topInset = 0`); `.om-detail-page--wide` for the two-pane measure on an expanded window. A body that is one lazy list takes the top and bottom gaps as list content padding instead.

Compose source: omega-kmp :ui, OmegaAdaptiveShell.kt, `OmegaDetailPage(scroll, topInset, wide, lazyBody)`
