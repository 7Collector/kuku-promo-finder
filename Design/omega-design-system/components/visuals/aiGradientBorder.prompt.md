Use the gradient border only on three things: the focus ring of the AI composer, an enabled AI send button, and a pill that is itself an AI control (a credit chip, an "Ask anything" bar); never on cards, list rows or ordinary buttons.

```html
<span class="om-ai-border" style="border-radius:var(--radius-full);padding:8px 16px">
  <i class="om-icon om-icon-sparkle om-gradient-sparkle"></i> Ask anything
</span>
```

Classes: `om-ai-border` draws a 2 px `--ai-gradient` ring around the element's own shape and fills the inside with the surface colour. `--ai-border-width` changes the ring width (default 2px); `--ai-border-fill` changes the inside fill (for example `var(--accent-container)`). The element supplies its own `border-radius`, padding and layout. The ring is static: it does not rotate or pulse. Do not put a shadow or a second border on the same element.

Compose source: omega-kmp :ui, AiGradientBorder.kt, `Modifier.aiGradientBorder(shape, fill, width = 2.dp, animated)` with `fill` as a Color or a Brush
