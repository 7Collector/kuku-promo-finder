# SectionHeader

Use above a section's content: the title in headline with at most one thing at its end. No rule beneath it; spacing separates sections.

```html
<div class="om-section-header">
  <h2 class="om-section-header__title">Homework</h2>
  <span class="om-section-header__count">3 pending</span>
</div>
```

- `.om-section-header__title`: headline, ink, up to two lines.
- `.om-section-header__count`: caption with tabular figures, ink 3, 12 from the title.
- `.om-section-header__action`: wrapper for a tertiary button, 8 from the title.
- `.om-section-header__trailing`: wrapper for any other trailing content, 12 from the title.
- Only one of count, action or trailing is drawn; trailing content wins, then the action, then the count.

Compose source: omega-kmp :ui, OmegaList.kt, SectionHeader(title, count, actionLabel, onAction, trailingContent); OmegaSurface.kt, OmegaSectionHeading(title, trailing, trailingContent)
