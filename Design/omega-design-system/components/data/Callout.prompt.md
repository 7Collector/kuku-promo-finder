# Callout

Use for a message that stays on the page, one per concern. The icon is the tone's own so meaning is never carried by colour alone.

```html
<div class="om-callout om-callout--info">
  <i class="om-icon om-icon-info-circle om-callout__icon"></i>
  <div class="om-callout__body">
    <p class="om-callout__title">PTM moved</p>
    <p class="om-callout__text">The parent-teacher meeting is now on Saturday at 10:00.</p>
    <span class="om-callout__action" role="button">View</span>
  </div>
</div>
```

- Tones: `--info`, `--help`, `--tip`, `--success`, `--warning`, `--danger`, `--neutral`. Container fill, radius lg, 16 padding, no border.
- `.om-callout__icon`: 20 px in the tone's strong colour, top-aligned. Override the glyph when needed (cloud-off for offline).
- `.om-callout__title` (optional): body strong. `.om-callout__text`: subhead. Both on-container.
- `.om-callout__action` (optional): a tertiary button, 48 tall, painted on-container rather than accent.

Compose source: omega-kmp :ui, OmegaStatus.kt, Callout(tone: Tone, text, title, actionLabel, onAction, icon = toneIcon(tone))
