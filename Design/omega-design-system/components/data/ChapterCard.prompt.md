# ChapterCard

Use for a syllabus chapter: number, title, coverage bar, then its sub-topics. The bar is the accent mark and the number is neutral; a subject family is not a tone.

```html
<div class="om-card om-chapter-card">
  <div class="om-chapter-card__header">
    <span class="om-chapter-card__number">7</span>
    <div class="om-chapter-card__heading"><p class="om-chapter-card__title">Introduction to Trigonometry</p><p class="om-chapter-card__meta">In progress · covered today</p></div>
  </div>
  <div class="om-progress" style="--progress:72%"><div class="om-progress__fill"></div></div>
  <div class="om-chapter-card__subtopics">…subtopic rows…</div>
</div>
```

- `.om-chapter-card__number`: 32 px square, radius md, sunken, ink 2, tabular figures.
- The progress bar has 12 above and below; sub-topic rows are 8 apart.
- A chapter with no sub-topics shows just the header and the bar.
- No variants and no tappable state in the source.

Compose source: omega-kmp :ui, SubtopicRow.kt, ChapterCard(number, title, meta, fraction, subtopics: List<Pair<String, SubtopicStatus>>)
