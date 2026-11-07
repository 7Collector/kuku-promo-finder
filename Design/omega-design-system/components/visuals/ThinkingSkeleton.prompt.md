Use the thinking skeleton while AI is producing an answer that will replace it; the label says in plain words what is being made, and the bars stay still.

```html
<div class="om-thinking-skeleton" role="status" aria-label="Building your deck">
  <div class="om-thinking-label"><i class="om-icon om-icon-sparkle om-gradient-sparkle"></i>Building your deck</div>
  <div class="om-thinking-bar"></div>
  <div class="om-thinking-bar"></div>
  <div class="om-thinking-bar"></div>
</div>
```

Classes: `om-thinking-skeleton` (column), `om-thinking-label` (16 px gradient sparkle and a caption in ink 2), `om-thinking-bar` (12 tall, radius xs, sunken; the three bars are 100%, 82% and 58% wide). Always exactly three bars. No shimmer and no pulse: the source draws them static. It usually sits inside an `om-ai-card` or directly on the page where the answer will appear.

Compose source: omega-kmp :ui, AiSurfaces.kt, `ThinkingSkeleton(label)`
