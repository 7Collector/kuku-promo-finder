Use these as the ground layer of a screen: both draw flat paper and nothing else, so AI screens and ordinary screens share one ground with no glow, gradient or blur behind the content.

```html
<div style="position:relative">
  <div class="om-ground-bloom" aria-hidden="true" style="position:absolute;inset:0"></div>
  <div style="position:relative">Screen content</div>
</div>
```

Classes: `om-ground-bloom` (the ground of ordinary screens) and `om-aurora` (the ground of AI screens); each is a block filled with the paper colour. Position the layer to fill its screen and put the content above it. The names are historical: neither draws a bloom or an aurora any more, and neither should be given one. Surfaces placed on them use the surface colour with no shadow.

Compose source: omega-kmp :ui, GroundBloom.kt, `GroundBloomBackground()`; AiSurfaces.kt, `AuroraBackground()`
