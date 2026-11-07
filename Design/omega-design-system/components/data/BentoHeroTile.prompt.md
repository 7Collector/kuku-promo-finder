# BentoHeroTile

Use on Home for the next lecture: the one dark block the screen has. A caption, the title and subtitle, the start time as a tabular figure, and a thin bar while a period runs. Nothing loops; the live state is said in the caption's words.

```html
<div class="om-board-card om-board-hero">
  <div class="om-board-hero__kicker-row"><span class="om-live-dot"></span><span class="om-board-hero__kicker">Now · ends in 14 min</span></div>
  <div class="om-board-hero__main">
    <div class="om-board-hero__text"><p class="om-board-hero__title">Physics</p><p class="om-board-hero__subtitle">Mr. Iyer · Room 204</p></div>
    <div class="om-board-hero__trailing"><span class="om-board-hero__figure">11:40</span><span class="om-board-hero__meta">45 min</span></div>
  </div>
  <div class="om-progress om-progress--on-board" style="--progress:68%"><div class="om-progress__fill"></div></div>
</div>
```

- `.om-live-dot`: a static 8 px dot (accent mark; the on-board accent inside a board card). Leave it out when `showLiveDot` is false.
- Leave the progress bar out when there is no period running.
- Add `.om-board-card--tappable` to make the whole board one target.
- Title and subtitle clamp at two lines; kicker, figure and meta stay on one.

Compose source: omega-kmp :ui, BentoTile.kt, BentoHeroTile(kicker, title, subtitle, trailingFigure, trailingMeta, progress: Float?, showLiveDot = true, onClick), PulsingDot(color, size = 8.dp)
