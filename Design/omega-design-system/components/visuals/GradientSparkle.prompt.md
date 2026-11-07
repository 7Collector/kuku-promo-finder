Use the gradient sparkle (or another glyph filled with the same gradient) as the small mark that says "this is AI"; it is one of the few places `--ai-gradient` may appear, and it is never used as decoration on non-AI content.

```html
<i class="om-icon om-icon-sparkle om-gradient-sparkle" style="--icon-size:16px"></i>
<i class="om-icon om-icon-book om-gradient-glyph" style="--icon-size:24px"></i>
```

Classes: `om-gradient-sparkle` (the sparkle icon filled with the AI gradient) and `om-gradient-glyph` (any `om-icon-NAME` filled with it); both go on the `om-icon` element and take their size from `--icon-size`. Usual sizes: 16 in a card kicker or a thinking label, 20 to 24 beside a title, 32 as a standalone mark. The gradient replaces the icon colour, so do not also set `color`. One gradient mark per block is enough.

Compose source: omega-kmp :ui, AiSurfaces.kt, `GradientSparkle(size)`, `GradientGlyph(icon, size)`
