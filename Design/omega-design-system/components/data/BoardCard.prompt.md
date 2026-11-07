# BoardCard

Use once per screen, for the one thing that matters most right now. Board fill, radius xl, 20 padding; text on it is on-board and on-board-2 only.

```html
<div class="om-board-card om-board-card--glow">
  <p class="om-title-medium">Unit test on Thursday</p>
  <p class="om-subhead" style="color:var(--on-board-2)">Physics, chapters 3 and 4</p>
</div>
```

- `.om-board-card`: the dark surface. No shadow.
- `.om-board-card--glow`: a soft radial highlight from the top-right corner, reaching 0.7 of the longer side. Decorative.
- `.om-board-card--tappable`: one target; `:active` or `.is-pressed` gives the 0.98 scale (the ripple is ink, so it barely shows on the board).
- Marks on the board use `--accent-mark-on-board`; danger text uses `--danger-on-board`; rules and tracks use `--board-rule`.

Compose source: omega-kmp :ui, BoardCard.kt, BoardCard(glow = false, onClick, contentDescription)
