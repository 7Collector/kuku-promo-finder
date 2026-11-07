# ScoreDisplay

Use inside a board card to show a score: the figure in display with tabular figures, a thin accent bar for the fraction, and a caption such as the date.

```html
<div class="om-board-card">
  <div class="om-score">
    <span class="om-score__figure">32/50</span>
    <div class="om-progress om-progress--on-board" style="--progress:64%"><div class="om-progress__fill"></div></div>
    <span class="om-score__caption">Physics unit test · Mon 21 Sep</span>
  </div>
</div>
```

- `.om-score`: a column with 8 between the parts.
- Leave the bar out for a score with no maximum (a grade).
- Leave the caption out when there is none.
- Only for use on the board: its colours are on-board and on-board-2.

Compose source: omega-kmp :ui, BoardCard.kt, ScoreDisplay(score, fraction: Float?, caption)
