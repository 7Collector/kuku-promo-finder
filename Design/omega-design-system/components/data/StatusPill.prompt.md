# StatusPill

Use for a live state that stands in its own right, such as Live or Last updated 23 seconds ago. It is a status badge at full radius that may wrap to two lines.

```html
<span class="om-status-pill om-status-pill--success"><span class="om-status-pill__dot"></span>Live</span>
<span class="om-status-pill om-status-pill--warning"><i class="om-icon om-icon-warning"></i>Last updated 4 minutes ago</span>
```

- Tones: `--info`, `--help`, `--tip`, `--success`, `--warning`, `--danger`, `--neutral`.
- `.om-status-pill__dot`: an 8 px dot in the tone's strong colour (the Live mark). It does not pulse.
- A 14 px icon instead of the dot; never both.
- Same metrics as the badge: 24 minimum height, 8 by 2 padding, caption.

Compose source: omega-kmp :ui, OmegaStatus.kt, StatusPill(tone: Tone, text, dot = false, icon)
