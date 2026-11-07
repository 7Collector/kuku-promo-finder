Use the ring as the AI avatar: a still accent-container disc with the gradient sparkle, which becomes a plain accent spinner only while something is actually in flight (an upload, an attachment being read).

```html
<span class="om-ai-ring" style="--ring-size:40px"><i class="om-icon om-icon-sparkle om-gradient-sparkle"></i></span>

<span class="om-ai-ring is-waiting" style="--ring-size:24px" role="status" aria-label="Uploading">
  <svg class="om-ai-ring-spinner" viewBox="0 0 19 19"><circle cx="9.5" cy="9.5" r="8.25" stroke-width="2.5" pathLength="100" stroke-dasharray="70 100"/></svg>
</span>
```

Classes: `om-ai-ring` (disc of `--ring-size`, default 40; the sparkle is 0.46 of that), `is-waiting` (no disc and no sparkle: the spinner alone), `om-ai-ring-spinner` (accent mark, stroke 2.5, drawn 2.5 inside the box on each side, so the viewBox is the size minus 5). The still form never moves, despite the name. The spinner is the only looping motion here and it stops under `prefers-reduced-motion`.

Compose source: omega-kmp :ui, AiSurfaces.kt, `SpinningGradientRing(size, ringInset = 2.5.dp, sparkleSize, rotationPeriodMillis = 7000, animated)`; a period under 3000 with `animated` gives the waiting form
