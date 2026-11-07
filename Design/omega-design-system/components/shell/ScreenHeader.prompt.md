# ScreenHeader and ScreenBackButton

A screen's header: it fills the scaffold's bar row (back chevron, actions, title) and draws the large title at the top of the content, which collapses into the bar once it scrolls under it. Tab roots pass no back. The back control is a chevron with no words in a 48 target; its glyph sits on the page margin, and its accessible name is "Back to ‹parent›".

```html
<div class="om-screen-bar-row">
  <button class="om-back-button" aria-label="Back to classes"><i class="om-icon om-icon-chevron-left"></i></button>
  <div class="om-screen-bar-title-slot"><div class="om-screen-bar-title om-screen-bar-title--copy">Mark attendance</div></div>
  <div class="om-screen-bar-actions"><!-- caller's 48 icon buttons --></div>
</div>
<!-- in the content -->
<div class="om-screen-header">
  <div class="om-screen-header-context">Class 7B · Mathematics</div>
  <h1 class="om-screen-header-title">Mark attendance</h1>
</div>
```

Variants: large title (default; the bar copy `.om-screen-bar-title--copy` shows only under `.om-screen-bar.is-collapsed`); pinned title (`largeTitle = false`: plain `.om-screen-bar-title`, no title in content) with an optional `.om-screen-bar-subtitle` that wraps in full and is never truncated; no back (`<span class="om-screen-bar-keyline"></span>` in place of the button); `title = null` (bar controls only); inline (`.om-screen-header-row` inside `.om-screen-header`, used when there is no scaffold bar, such as a detail pane beside its list).

Compose source: omega-kmp :ui, ScreenScaffold.kt, `ScreenHeader(title, backLabel, onBack, actions, largeTitle, context, subtitle)`, `ScreenBackButton(description, onClick, tint)`, `backDescription`, `LocalBackWording`
