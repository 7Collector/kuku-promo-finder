# StatusBadge

Use for a status word such as Submitted, Due today or On leave. In a list row it goes in the meta row above the title, never beside wrapping text.

```html
<span class="om-status-badge om-status-badge--warning">Due today</span>
<span class="om-status-badge om-status-badge--danger"><i class="om-icon om-icon-octagon-alert"></i>Overdue</span>
```

- Tones: `--info`, `--help`, `--tip`, `--success`, `--warning`, `--danger`, `--neutral`. Container fill, on-container text.
- Radius xs, 24 minimum height, 8 by 2 padding, caption, one line, no border.
- Optional 14 px icon; the tone's own are info-circle, help, lightbulb, check-circle, warning, octagon-alert, and info-circle for neutral.
- Sentence case always.

Compose source: omega-kmp :ui, OmegaStatus.kt, StatusBadge(tone: Tone, text, icon), toneIcon(tone)
