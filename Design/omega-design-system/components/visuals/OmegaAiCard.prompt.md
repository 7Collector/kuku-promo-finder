Use the AI card for any block of content that AI wrote or offers to write; the kicker line with the gradient sparkle is required and is the only AI mark, so the card itself stays a plain surface with no gradient frame.

```html
<section class="om-ai-card">
  <p class="om-ai-card-kicker"><i class="om-icon om-icon-sparkle om-gradient-sparkle"></i>Summary written by AI</p>
  <p>Attendance held steady this week. Two students need a call home.</p>
</section>

<button class="om-ai-card is-clickable" type="button">
  <span class="om-ai-card-kicker"><i class="om-icon om-icon-sparkle om-gradient-sparkle"></i>3 things AI noticed this week</span>
  <span>Two students dropped sharply</span>
</button>
```

Classes: `om-ai-card` (surface, radius lg, padding 16, no border, no shadow), `om-ai-card-kicker` (16 px sparkle, gap 8, caption in ink 2, with 8 below it before the content), `is-clickable` (the whole card is one target, at least 48 tall, scales to 0.98 while pressed). The kicker is plain sentence-case words that say what the AI did. Content is whatever the caller puts in: body text, rows, a button.

Compose source: omega-kmp :ui, OmegaAiCard.kt, `OmegaAiCard(kicker, contentPadding, onClick, content)`
