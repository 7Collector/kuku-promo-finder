# SubtopicRow

Use for one sub-topic line inside a chapter card: state ring, title, state word. The three states are three shapes (filled with a tick, filled, hollow), not three hues, and the row announces as one thing.

```html
<div class="om-subtopic-row om-subtopic-row--done" aria-label="Trigonometric ratios, Done">
  <span class="om-status-ring om-status-ring--done"><i class="om-icon om-icon-check"></i></span>
  <span class="om-subtopic-row__title">Trigonometric ratios</span>
  <span class="om-subtopic-row__state">Done</span>
</div>
```

- `--done`: success ring and fill with a surface tick; title ink 3; state word in success.
- `--started`: accent ring on the accent container, no tick; title ink; state word in accent.
- `--not-started`: outline ring, hollow; title ink 2; state word in outline.
- `.om-status-ring` (18 px, 2 px stroke, 10 px tick) is usable on its own with the same three modifiers; never label it separately.
- Read-only: the row has no pressed or selected state.

Compose source: omega-kmp :ui, SubtopicRow.kt, SubtopicRow(title, status: SubtopicStatus), OmegaStatusRing(status); OmegaColor.kt, subtopicVisuals(status)
