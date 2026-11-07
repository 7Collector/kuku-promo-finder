# StackedCardDeck

Use for a short queue that needs the user, where only the front card is actionable. A tap opens the item and does not dismiss it; dismissing is the swipe's job. Depth is offset, scale and opacity together.

```html
<div class="om-card-deck" aria-label="3 items need you">
  <div class="om-deck-card om-deck-card--depth-2" aria-hidden="true">…</div>
  <div class="om-deck-card om-deck-card--depth-1" aria-hidden="true">…</div>
  <div class="om-deck-card om-deck-card--front" role="button">
    <div class="om-deck-card__meta-row"><span class="om-deck-card__kicker">Homework due</span><span class="om-status-badge om-status-badge--neutral">3</span></div>
    <p class="om-deck-card__title">Chemistry worksheet, Ch. 3</p>
    <p class="om-deck-card__body">Submit by tonight 11:59 PM</p>
    <p class="om-deck-card__cta">Open homework</p>
  </div>
</div>
```

- Draw at most three cards. `.om-card-deck--two` and `.om-card-deck--one` set the bottom room for fewer.
- `--depth-1`: 6 px down, 0.96 scale, 0.88 opacity. `--depth-2`: 12 px, 0.92, 0.76. All cards are as tall as the tallest.
- Each card: surface, radius lg, a 1 px hairline edge, no shadow. Badge and action line are optional; `__body--full` lifts the three-line clamp.
- Front card `:active` or `.is-pressed`: ink ripple, no scale.
- Swipe: wrap the front card in `.om-card-deck__front` with `.om-card-deck__stamps` behind it; set `--drag-x` on the wrapper and `--stamp-opacity` on the stamp being revealed.
- `.om-card-deck-empty`: the 174 px placeholder with a success tick and a label such as All caught up.

Compose source: omega-kmp :ui, StackedCardDeck.kt, StackedCardDeck(cards: List<StackedCard>, onTap, emptyLabel, swipe: StackedCardSwipeConfig?, summary, bodyMaxLines = 3), StackedCardMetrics
