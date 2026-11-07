Use progress dots to show where someone is in a short fixed run of steps or cards (12 at most); beyond 12 segments nothing is drawn, so pair long runs with a count in words instead.

```html
<span class="om-progress-dots" aria-hidden="true">
  <i class="om-progress-dot is-passed"></i>
  <i class="om-progress-dot is-current"></i>
  <i class="om-progress-dot"></i>
</span>
```

Classes: `om-progress-dots` (row, gap 5; `--dots-accent` and `--dots-faint` set the two colours, default accent mark and outline), `om-progress-dot` (5 tall, 6 wide, faint), `is-passed` (10 wide, accent), `is-current` (20 wide, accent). Exactly one dot is current. The row is decorative: the screen states the position in words nearby ("Card 3 of 5").

Compose source: omega-kmp :ui, ProgressBarDots.kt, `ProgressBarDots(segments, accent, faint)`, `ProgressSegments.forSteps`, `ProgressSegments.forCards`
