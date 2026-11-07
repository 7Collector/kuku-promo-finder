# TimelineRow

Use for one item of the day's routine on a rail. Rows sit on paper, not in cards, and state is carried by shape and words: a live row has an accent node and rail and says Now; a private task has a dashed node.

```html
<div class="om-timeline-row om-timeline-row--live">
  <div class="om-timeline-row__time"><span class="om-timeline-row__start">11:40</span><span class="om-timeline-row__duration">45 min</span></div>
  <div class="om-timeline-row__rail"><span class="om-timeline-row__node"></span></div>
  <div class="om-timeline-row__body">
    <div class="om-timeline-row__flags"><span class="om-timeline-row__flag">Now</span><span class="om-timeline-row__kind">Lecture</span></div>
    <span class="om-timeline-row__title">Physics</span>
    <span class="om-timeline-row__subtitle">Room 204 · Mr. Iyer</span>
  </div>
</div>
```

- Default: outline node, hairline rail.
- `.om-timeline-row--live`: accent node and rail; the flag (Now) is accent text.
- Next: add a `__flag` reading Next; the node stays neutral and the flag is ink 2.
- `.om-timeline-row--private`: a hollow node with a dashed ring.
- `.om-timeline-row--tappable` with `:active` or `.is-pressed`: ink ripple only.
- Leave `__flags` out when there is no kind and no flag; write the kind in sentence case. The time column is at least 56 wide and never truncates.
- The add row at the end of a routine is a tertiary button with a plus icon, not a timeline row.

Compose source: omega-kmp :ui, TimelineRow.kt, TimelineRow(time, duration, kind, title, subtitle, isLive, isNext, isPrivate, onClick, liveLabel = "Now", nextLabel = "Next"), TimelineAddRow(label, onClick)
