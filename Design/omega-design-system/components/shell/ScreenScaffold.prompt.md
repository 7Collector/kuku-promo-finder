# ScreenScaffold

The frame of every screen: a pinned bar on opaque paper and a body held to the reading measure (640, centred). The bar owns the status bar and is always drawn, at least as a strip; its 56 row appears only when a ScreenHeader claims it or the host reserves it. The bottom insets are not handled here: exactly one element per screen owns them.

```html
<div class="om-screen">
  <header class="om-screen-bar is-collapsed"><div class="om-screen-bar-row">…</div></header>
  <div class="om-screen-pinned-header is-scrolled"><div class="om-screen-pinned-header-inner">…</div></div>
  <div class="om-screen-body"><div class="om-screen-content">…</div></div>
</div>
```

Variants and states: `.om-screen-bar.is-scrolled` (hairline once the body leaves the top), `.om-screen-bar.is-collapsed` (large title scrolled under the bar: hairline plus the bar title), `.om-screen-pinned-header` (a tab root's pinned header; `.is-scrolled` moves the hairline to its foot, so do not also set it on the bar), `.om-screen-content--tab-root` (24 top gap under the bare strip; default is 8 under the bar row), `.om-screen-content--flush-top`. Page margin is `--page-margin` (20, or 24 from 400 wide); set `--status-bar-inset` for the system inset.

Compose source: omega-kmp :ui, ScreenScaffold.kt, `ScreenScaffold(scrollState, maxContentWidth, reserveBarRow, pinnedHeader, lazyBodyPadding)`, `ScreenBarScrollSource`, `screenBodyTopGap`, `ScreenBarRowHeight`
